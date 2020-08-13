from typing import Optional
from typing import Tuple

from pythongame.core.common import ConsumableType, Sprite, ItemId
from pythongame.core.common import Millis, HeroId, AbstractScene, SceneTransition
from pythongame.core.entity_creation import create_player_state_as_initial, create_hero_world_entity
from pythongame.core.game_state import GameState
from pythongame.core.global_path_finder import init_global_path_finder
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.npc_behaviors import get_quest
from pythongame.core.quests import QuestId
from pythongame.core.world_behavior import ChallengeBehavior, StoryBehavior
from pythongame.map_file import load_map_from_json_file
from pythongame.player_file import SavedPlayerState
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import GameUiView
from pythongame.world_init_util import register_game_engine_observers, \
    register_game_state_observers


class InitFlags:
    def __init__(self,
                 map_file_path: Optional[str],
                 picked_hero: Optional[HeroId],
                 saved_player_state: Optional[SavedPlayerState],
                 hero_start_level: Optional[int],
                 start_money: Optional[int],
                 character_file: Optional[str]):
        self.map_file_path = map_file_path
        self.picked_hero = picked_hero
        self.saved_player_state: SavedPlayerState = saved_player_state
        self.hero_start_level = hero_start_level
        self.start_money = start_money
        self.character_file: str = character_file

    def __repr__(self):
        return "(" + self.map_file_path + ", " + str(self.picked_hero) + ", " + \
               str(self.saved_player_state) + ", " + str(self.hero_start_level) + ", " + str(self.start_money) + ")"


class CreatingWorldScene(AbstractScene):
    def __init__(
            self,
            scene_factory: AbstractSceneFactory,
            camera_size: Tuple[int, int], ui_view: GameUiView,
            flags: InitFlags):
        self.scene_factory = scene_factory
        self.camera_size = camera_size
        self.ui_view = ui_view

        # map hero money level saved
        self.flags: InitFlags = flags

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:

        saved_player_state = self.flags.saved_player_state
        hero_start_level = self.flags.hero_start_level
        start_money = self.flags.start_money
        picked_hero_id = self.flags.picked_hero
        map_file_path = self.flags.map_file_path
        character_file = self.flags.character_file
        if saved_player_state:
            hero_from_saved_state = HeroId[saved_player_state.hero_id]
            if picked_hero_id is not None and picked_hero_id != hero_from_saved_state:
                raise Exception("Mismatch! Hero from saved state: " + str(hero_from_saved_state) + ", but picked hero: "
                                + str(picked_hero_id))
            picked_hero_id = hero_from_saved_state
        total_time_played_on_character = saved_player_state.total_time_played_on_character if saved_player_state else 0

        # NPC's share a "global path finder" that needs to be initialized before we start creating NPCs.
        # TODO This is very messy
        path_finder = init_global_path_finder()
        game_state = self._load_map_and_setup_game_state(map_file_path, picked_hero_id)
        path_finder.set_grid(game_state.pathfinder_wall_grid)

        # Must center camera before notifying player position as it affects which walls are shown on the minimap
        game_state.center_camera_on_player()
        self.ui_view.on_world_area_updated(game_state.game_world.entire_world_area)
        self.ui_view.update_hero(game_state.player_state.hero_id)

        game_engine = GameEngine(game_state, self.ui_view.info_message)

        register_game_engine_observers(game_engine, self.ui_view)
        register_game_state_observers(game_state, self.ui_view, include_player_state=True)

        if saved_player_state:
            game_engine.gain_levels(saved_player_state.level - 1)
            game_state.player_state.gain_exp(saved_player_state.exp)
            item_ids_in_inventory = [ItemId.from_stats_string(item_stats_and_name[0], item_stats_and_name[1])
                                     if item_stats_and_name
                                     else None
                                     for item_stats_and_name in saved_player_state.items]
            game_engine.fill_item_inventory(item_ids_in_inventory)
            consumable_slots = {int(slot_number): [ConsumableType[c] for c in consumables]
                                for (slot_number, consumables) in saved_player_state.consumables_in_slots.items()}
            game_state.player_state.consumable_inventory.set_slots(consumable_slots)
            game_state.player_state.modify_money(saved_player_state.money)
            for portal in game_state.game_world.portals:
                if portal.portal_id.name in saved_player_state.enabled_portals:
                    sprite = saved_player_state.enabled_portals[portal.portal_id.name]
                    game_engine.activate_portal(portal, Sprite[sprite])
            for tier_index, option_index in enumerate(saved_player_state.talent_tier_choices):
                if option_index is not None:
                    pick_talent(game_state, tier_index, option_index)
            for completed_quest in saved_player_state.completed_quests:
                quest = get_quest(QuestId[completed_quest])
                game_state.player_state.start_quest(quest)
                game_state.player_state.complete_quest(quest)
            for active_quest in saved_player_state.active_quests:
                quest = get_quest(QuestId[active_quest])
                game_state.player_state.start_quest(quest)
        else:
            if hero_start_level > 1:
                game_engine.gain_levels(hero_start_level - 1)
            if start_money > 0:
                game_state.player_state.modify_money(start_money)

        # When loading from a savefile a bunch of messages are generated (levelup, learning talents, etc), but they
        # are irrelevant, since we're loading an exiting character
        self.ui_view.info_message.clear_messages()

        # Talent toggle is highlighted when new talents are unlocked, but we don't want it to be highlighted on startup
        # when loading from a savefile
        self.ui_view.remove_highlight_from_talent_toggle()

        # We need to handle the initial state (allocating input keys, updating UI, etc)
        game_engine.on_abilities_updated()

        if map_file_path == 'resources/maps/challenge.json':
            world_behavior = ChallengeBehavior(
                self.scene_factory, game_state, self.ui_view.info_message, game_engine, self.flags)
        else:
            world_behavior = StoryBehavior(self.scene_factory, game_engine, game_state, self.ui_view)

        new_hero_was_created = saved_player_state is None
        playing_scene = self.scene_factory.playing_scene(
            game_state, game_engine, world_behavior, self.ui_view, new_hero_was_created, character_file,
            total_time_played_on_character)
        return SceneTransition(playing_scene)

    def _load_map_and_setup_game_state(self, map_file_path: str, picked_hero_id: HeroId) -> GameState:
        map_data = load_map_from_json_file(map_file_path)
        game_world = map_data.game_world
        game_world.player_entity = create_hero_world_entity(picked_hero_id, map_data.player_position)
        enabled_portals = {portal.portal_id: portal.world_entity.sprite for portal in game_world.portals
                           if portal.is_enabled}
        return GameState(game_world=game_world,
                         camera_size=self.camera_size,
                         player_state=create_player_state_as_initial(picked_hero_id, enabled_portals),
                         is_dungeon=False,
                         player_spawn_position=map_data.player_position)
