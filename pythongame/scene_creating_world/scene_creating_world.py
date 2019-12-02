from typing import Optional, Callable
from typing import Tuple

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import ItemType, \
    ConsumableType, Sprite
from pythongame.core.common import Millis, HeroId, BuffType, AbstractScene, SceneTransition
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.world_behavior import ChallengeBehavior, StoryBehavior, AbstractWorldBehavior
from pythongame.map_file import create_game_state_from_json_file
from pythongame.player_file import SavedPlayerState
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView


class InitFlags:
    def __init__(self, map_file_path: Optional[str], picked_hero: Optional[HeroId],
                 saved_player_state: Optional[SavedPlayerState],
                 hero_start_level: int, start_money: int):
        self.map_file_path = map_file_path
        self.picked_hero = picked_hero
        self.saved_player_state = saved_player_state
        self.hero_start_level = hero_start_level
        self.start_money = start_money

    def __repr__(self):
        return "(" + self.map_file_path + ", " + str(self.picked_hero) + ", " + \
               str(self.saved_player_state) + ", " + str(self.hero_start_level) + ", " + str(self.start_money) + ")"


class CreatingWorldScene(AbstractScene):
    def __init__(
            self,
            playing_scene: Callable[
                [GameState, GameEngine, AbstractWorldBehavior, GameUiState, GameUiView, bool], AbstractScene],
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

        ui_state = GameUiState()
        game_state = create_game_state_from_json_file(
            self.camera_size, self.flags.map_file_path, self.flags.picked_hero)
        game_engine = GameEngine(game_state, ui_state)
        game_state.player_state.exp_was_updated.register_observer(self.ui_view.on_player_exp_updated)
        game_state.player_state.talents_were_updated.register_observer(self.ui_view.on_talents_updated)
        game_state.player_state.notify_talent_observers()  # Must notify the initial state
        game_state.player_movement_speed_was_updated.register_observer(self.ui_view.on_player_movement_speed_updated)
        game_state.notify_movement_speed_observers()  # Must notify the initial state
        game_state.player_state.stats_were_updated.register_observer(self.ui_view.on_player_stats_updated)
        game_state.player_state.notify_stats_observers()  # Must notify the initial state
        game_engine.talent_was_unlocked.register_observer(self.ui_view.on_talent_was_unlocked)
        game_state.player_state.money_was_updated.register_observer(self.ui_view.on_money_updated)
        game_state.player_state.notify_money_observers()  # Must notify the initial state
        game_state.player_state.abilities_were_updated.register_observer(self.ui_view.on_abilities_updated)
        game_state.player_state.notify_ability_observers()  # Must notify the initial state
        game_state.player_state.cooldowns_were_updated.register_observer(self.ui_view.on_cooldowns_updated)
        game_state.player_state.health_resource.value_was_updated.register_observer(self.ui_view.on_health_updated)
        game_state.player_state.mana_resource.value_was_updated.register_observer(self.ui_view.on_mana_updated)
        game_state.player_state.buffs_were_updated.register_observer(self.ui_view.on_buffs_updated)

        if self.flags.map_file_path == 'resources/maps/challenge.json':
            world_behavior = ChallengeBehavior(
                self.picking_hero_scene, self.challenge_complete_scene, game_state, ui_state, game_engine, self.flags)
        else:
            world_behavior = StoryBehavior(self.victory_screen_scene, game_state, ui_state)

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

        allocate_input_keys_for_abilities(game_state.player_state.abilities)

        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))

        new_hero_was_created = saved_player_state is None

        playing_scene = self.playing_scene(game_state, game_engine, world_behavior, ui_state, self.ui_view,
                                           new_hero_was_created)
        return SceneTransition(playing_scene)
