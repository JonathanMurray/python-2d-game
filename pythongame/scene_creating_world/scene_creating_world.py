from typing import Optional, Callable
from typing import Tuple

from pythongame.core.common import ItemType, \
    ConsumableType, Sprite, Observable
from pythongame.core.common import Millis, HeroId, AbstractScene, SceneTransition
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.entity_creation import set_global_path_finder
from pythongame.core.footsteps import play_or_stop_footstep_sounds
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.world_behavior import ChallengeBehavior, StoryBehavior, AbstractWorldBehavior
from pythongame.map_file import load_map_from_json_file
from pythongame.player_file import SavedPlayerState
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_view import GameUiView


class InitFlags:
    def __init__(self,
                 map_file_path: Optional[str],
                 picked_hero: Optional[HeroId],
                 saved_player_state: Optional[SavedPlayerState],
                 hero_start_level: int,
                 start_money: int,
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
            playing_scene: Callable[
                [GameState, GameEngine, AbstractWorldBehavior, GameUiView, bool, Optional[str], Millis],
                AbstractScene],
            picking_hero_scene: Callable[[InitFlags], AbstractScene],
            challenge_complete_scene: Callable[[Millis], AbstractScene],
            victory_screen_scene: Callable[[], AbstractScene],
            camera_size: Tuple[int, int], ui_view: GameUiView,
            flags: InitFlags):
        self.playing_scene = playing_scene
        self.picking_hero_scene = picking_hero_scene
        self.challenge_complete_scene = challenge_complete_scene
        self.victory_screen_scene = victory_screen_scene
        self.camera_size = camera_size
        self.ui_view = ui_view

        # map hero money level saved
        self.flags: InitFlags = flags

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:

        saved_player_state = self.flags.saved_player_state
        hero_start_level = self.flags.hero_start_level
        start_money = self.flags.start_money
        picked_hero = self.flags.picked_hero
        map_file_path = self.flags.map_file_path
        character_file = self.flags.character_file

        if saved_player_state:
            hero_from_saved_state = HeroId[saved_player_state.hero_id]
            if picked_hero is not None and picked_hero != hero_from_saved_state:
                raise Exception("Mismatch! Hero from saved state: " + str(hero_from_saved_state) + ", but picked hero: "
                                + str(picked_hero))
            picked_hero = hero_from_saved_state

        total_time_played_on_character = saved_player_state.total_time_played_on_character if saved_player_state else 0

        # NPC's share a "global path finder" that needs to be initialized before we start creating NPCs.
        # TODO This is very messy
        path_finder = GlobalPathFinder()
        set_global_path_finder(path_finder)

        map_data = load_map_from_json_file(self.camera_size, map_file_path, picked_hero)

        path_finder.set_grid(map_data.game_state.pathfinder_wall_grid)

        game_state = map_data.game_state
        game_engine = GameEngine(game_state, self.ui_view.info_message)
        game_state.player_state.exp_was_updated.register_observer(self.ui_view.on_player_exp_updated)
        game_state.player_state.talents_were_updated.register_observer(self.ui_view.on_talents_updated)
        game_state.player_state.notify_talent_observers()  # Must notify the initial state
        game_state.player_movement_speed_was_updated.register_observer(self.ui_view.on_player_movement_speed_updated)
        game_state.notify_movement_speed_observers()  # Must notify the initial state
        game_state.player_state.stats_were_updated.register_observer(self.ui_view.on_player_stats_updated)
        game_state.player_state.notify_stats_observers()  # Must notify the initial state
        game_engine.talent_was_unlocked.register_observer(self.ui_view.on_talent_was_unlocked)
        game_engine.ability_was_clicked.register_observer(self.ui_view.on_ability_was_clicked)
        game_engine.consumable_was_clicked.register_observer(self.ui_view.on_consumable_was_clicked)
        game_state.player_state.money_was_updated.register_observer(self.ui_view.on_money_updated)
        game_state.player_state.notify_money_observers()  # Must notify the initial state
        game_state.player_state.abilities_were_updated.register_observer(self.ui_view.on_abilities_updated)
        game_state.player_state.notify_ability_observers()  # Must notify the initial state
        game_state.player_state.cooldowns_were_updated.register_observer(self.ui_view.on_cooldowns_updated)
        game_state.player_state.health_resource.value_was_updated.register_observer(self.ui_view.on_health_updated)
        game_state.player_state.mana_resource.value_was_updated.register_observer(self.ui_view.on_mana_updated)
        game_state.player_state.buffs_were_updated.register_observer(self.ui_view.on_buffs_updated)
        game_state.player_state.quests_were_updated.register_observer(self.ui_view.on_player_quests_updated)
        game_state.player_entity.movement_changed = Observable()
        game_state.player_entity.movement_changed.register_observer(play_or_stop_footstep_sounds)
        game_state.player_entity.position_changed = Observable()
        game_state.player_entity.position_changed.register_observer(self.ui_view.on_player_position_updated)
        game_state.player_entity.position_changed.register_observer(
            lambda _: self.ui_view.on_walls_seen([w.get_position() for w in game_state.get_walls_in_sight_of_player()]))
        self.ui_view.on_world_area_updated(game_state.entire_world_area)
        # Must center camera before notifying player position as it affects which walls are shown on the minimap
        game_state.center_camera_on_player()
        game_state.player_entity.notify_position_observers()  # Must notify the initial state

        if map_file_path == 'resources/maps/challenge.json':
            world_behavior = ChallengeBehavior(
                self.picking_hero_scene, self.challenge_complete_scene, game_state, self.ui_view.info_message,
                game_engine, self.flags)
        else:
            world_behavior = StoryBehavior(self.victory_screen_scene, game_state, self.ui_view.info_message)

        if saved_player_state:
            game_engine.gain_levels(saved_player_state.level - 1)
            game_state.player_state.gain_exp(saved_player_state.exp)
            game_engine.set_item_inventory([ItemType[item] if item else None for item in saved_player_state.items])
            game_state.player_state.consumable_inventory = ConsumableInventory(
                {int(slot_number): [ConsumableType[c] for c in consumables] for (slot_number, consumables)
                 in saved_player_state.consumables_in_slots.items()}
            )
            game_state.player_state.modify_money(saved_player_state.money)
            for portal in game_state.portals:
                if portal.portal_id.name in saved_player_state.enabled_portals:
                    sprite = saved_player_state.enabled_portals[portal.portal_id.name]
                    portal.activate(Sprite[sprite])
            for tier_index, option_index in enumerate(saved_player_state.talent_tier_choices):
                if option_index is not None:
                    pick_talent(game_state, tier_index, option_index)
        else:
            if hero_start_level > 1:
                game_engine.gain_levels(hero_start_level - 1)
            if start_money > 0:
                game_state.player_state.modify_money(start_money)

        game_state.player_state.item_inventory.was_updated.register_observer(self.ui_view.on_inventory_updated)
        game_state.player_state.item_inventory.notify_observers()  # Must notify the initial state
        game_state.player_state.consumable_inventory.was_updated.register_observer(self.ui_view.on_consumables_updated)
        game_state.player_state.consumable_inventory.notify_observers()  # Must notify the initial state
        self.ui_view.update_hero(game_state.player_state.hero_id)

        # When loading from a savefile a bunch of messages are generated (levelup, learning talents, etc), but they
        # are irrelevant, since we're loading an exiting character
        self.ui_view.info_message.clear_messages()

        # Talent toggle is highlighted when new talents are unlocked, but we don't want it to be highlighted on startup
        # when loading from a savefile
        self.ui_view.remove_highlight_from_talent_toggle()

        allocate_input_keys_for_abilities(game_state.player_state.abilities)

        new_hero_was_created = saved_player_state is None
        playing_scene = self.playing_scene(
            game_state, game_engine, world_behavior, self.ui_view, new_hero_was_created, character_file,
            total_time_played_on_character)
        return SceneTransition(playing_scene)
