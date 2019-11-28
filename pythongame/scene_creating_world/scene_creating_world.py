from typing import Optional
from typing import Tuple

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import ItemType, \
    ConsumableType, Sprite
from pythongame.core.common import SceneId, Millis, HeroId, BuffType, get_random_hint, \
    SoundId, HeroUpgrade, AbstractScene, SceneTransition
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.game_data import allocate_input_keys_for_abilities, ITEMS
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.item_effects import get_item_effect, try_add_item_to_inventory
from pythongame.core.sound_player import play_sound
from pythongame.core.world_behavior import AbstractWorldBehavior
from pythongame.map_file import create_game_state_from_json_file
from pythongame.player_file import SavedPlayerState
from pythongame.scenes_game.game_engine import GameEngine, EngineEvent
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


class StoryBehavior(AbstractWorldBehavior):

    def __init__(self, game_state: GameState, ui_state: GameUiState):
        self.game_state = game_state
        self.ui_state = ui_state

    def on_startup(self, new_hero_was_created: bool):
        self.ui_state.set_message("Hint: " + get_random_hint())
        if new_hero_was_created:
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.HEALTH_LESSER)
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.HEALTH_LESSER)
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.MANA_LESSER)
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.MANA_LESSER)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        if self.game_state.player_state.has_upgrade(HeroUpgrade.HAS_WON_GAME):
            return SceneTransition(SceneId.VICTORY_SCREEN, None)

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        if event == EngineEvent.PLAYER_DIED:
            self.game_state.player_entity.set_position(self.game_state.player_spawn_position)
            self.game_state.player_state.health_resource.set_to_partial_of_max(0.5)
            self.game_state.player_state.lose_exp_from_death()
            self.game_state.player_state.force_cancel_all_buffs()
            self.ui_state.set_message("Lost exp from dying")
            play_sound(SoundId.EVENT_PLAYER_DIED)
            self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        return None


class ChallengeBehavior(AbstractWorldBehavior):

    def __init__(self, game_state: GameState, ui_state: GameUiState, game_engine: GameEngine, init_flags: InitFlags):
        self.game_state = game_state
        self.ui_state = ui_state
        self.game_engine = game_engine
        self.total_time_played = 0
        self.init_flags = init_flags

    def on_startup(self, new_hero_was_created: bool):
        self.ui_state.set_message("Challenge starting...")
        if new_hero_was_created:
            self.game_state.player_state.money += 100
            self.game_engine.gain_levels(4)

            consumables = [ConsumableType.HEALTH,
                           ConsumableType.HEALTH,
                           ConsumableType.MANA,
                           ConsumableType.MANA,
                           ConsumableType.SPEED,
                           ConsumableType.POWER]
            for consumable_type in consumables:
                self.game_state.player_state.consumable_inventory.add_consumable(consumable_type)
            items = [ItemType.LEATHER_COWL, ItemType.LEATHER_ARMOR, ItemType.WOODEN_SWORD, ItemType.WOODEN_SHIELD]
            for item_type in items:
                self._equip_item_on_startup(item_type)

    def _equip_item_on_startup(self, item_type):
        data = ITEMS[item_type]
        item_effect = get_item_effect(item_type)
        try_add_item_to_inventory(self.game_state, item_effect, data.item_equipment_category)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        self.total_time_played += time_passed
        return None

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        if event == EngineEvent.PLAYER_DIED:
            return SceneTransition(SceneId.PICKING_HERO, self.init_flags)
        elif event == EngineEvent.ENEMY_DIED:
            num_enemies = len([npc for npc in self.game_state.non_player_characters if npc.is_enemy])
            if num_enemies == 0:
                return SceneTransition(SceneId.CHALLENGE_COMPLETE_SCREEN, self.total_time_played)
            self.ui_state.set_message(str(num_enemies) + " enemies remaining")
        return None


class CreatingWorldScene(AbstractScene):
    def __init__(self, camera_size: Tuple[int, int], ui_view: GameUiView):
        self.camera_size = camera_size
        self.ui_view = ui_view

        self.flags: InitFlags = None

    def initialize(self, flags: InitFlags):
        self.flags = flags  # map hero money level saved

    def run_one_frame(self, _time_passed: Millis, _fps_string: str) -> Optional[SceneTransition]:

        saved_player_state = self.flags.saved_player_state
        hero_start_level = self.flags.hero_start_level
        start_money = self.flags.start_money

        ui_state = GameUiState()
        game_state = create_game_state_from_json_file(
            self.camera_size, self.flags.map_file_path, self.flags.picked_hero)
        game_engine = GameEngine(game_state, ui_state)
        game_state.player_state.exp_was_updated.register_observer(self.ui_view.handle_event)
        game_state.player_state.talents_were_updated.register_observer(self.ui_view.handle_event)
        game_state.player_movement_speed_was_updated.register_observer(self.ui_view.handle_event)
        game_state.notify_movement_speed_observers()  # Must notify the initial state
        game_state.player_state.stats_were_updated.register_observer(self.ui_view.handle_event)
        game_state.player_state.notify_stats_observers()  # Must notify the initial state
        game_engine.player_abilities_were_updated.register_observer(self.ui_view.handle_event)
        if self.flags.map_file_path == 'resources/maps/challenge.json':
            world_behavior = ChallengeBehavior(game_state, ui_state, game_engine, self.flags)
        else:
            world_behavior = StoryBehavior(game_state, ui_state)

        if saved_player_state:
            game_engine.gain_levels(saved_player_state.level - 1)
            game_state.player_state.gain_exp(saved_player_state.exp)
            game_engine.set_item_inventory([ItemType[item] if item else None for item in saved_player_state.items])
            game_state.player_state.consumable_inventory = ConsumableInventory(
                {int(slot_number): [ConsumableType[c] for c in consumables] for (slot_number, consumables)
                 in saved_player_state.consumables_in_slots.items()}
            )
            game_state.player_state.money += saved_player_state.money
            for portal in game_state.portals:
                if portal.portal_id.name in saved_player_state.enabled_portals:
                    sprite = saved_player_state.enabled_portals[portal.portal_id.name]
                    portal.activate(Sprite[sprite])
            for index in saved_player_state.chosen_talent_option_indices:
                pick_talent(game_state, index)
        else:
            if hero_start_level > 1:
                game_engine.gain_levels(hero_start_level - 1)
            if start_money > 0:
                game_state.player_state.money += start_money

        game_state.player_state.item_inventory.was_updated.register_observer(self.ui_view.handle_event)
        game_state.player_state.item_inventory.notify_observers()  # Must notify the initial state
        game_state.player_state.consumable_inventory.was_updated.register_observer(self.ui_view.handle_event)
        game_state.player_state.consumable_inventory.notify_observers()  # Must notify the initial state
        self.ui_view.update_hero(game_state.player_state.hero_id)

        allocate_input_keys_for_abilities(game_state.player_state.abilities)
        game_engine.notify_ability_observers()  # Must notify the initial state

        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))

        new_hero_was_created = saved_player_state is None
        scene_transition_data = (game_state, game_engine, world_behavior, ui_state, self.ui_view, new_hero_was_created)
        return SceneTransition(SceneId.PLAYING, scene_transition_data)
