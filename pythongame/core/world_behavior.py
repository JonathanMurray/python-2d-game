from typing import Optional, Callable, Any

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import ConsumableType, AbstractScene
from pythongame.core.common import ItemType
from pythongame.core.common import Millis, BuffType, get_random_hint, \
    SoundId, HeroUpgrade, SceneTransition
from pythongame.core.game_data import ITEMS
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import get_item_effect, try_add_item_to_inventory
from pythongame.core.sound_player import play_sound
from pythongame.scenes_game.game_engine import EngineEvent
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState


class AbstractWorldBehavior:

    def on_startup(self, new_hero_was_created: bool):
        pass

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        pass

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        pass


class StoryBehavior(AbstractWorldBehavior):

    def __init__(self, victory_screen_scene: Callable[[], AbstractScene], game_state: GameState, ui_state: GameUiState):
        self.victory_screen_scene = victory_screen_scene
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
            return SceneTransition(self.victory_screen_scene())

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

    def __init__(self, picking_hero_scene: Callable[[Any], AbstractScene],
                 challenge_complete_scene: Callable[[Millis], AbstractScene],
                 game_state: GameState,
                 ui_state: GameUiState,
                 game_engine: GameEngine,
                 init_flags):
        self.picking_hero_scene = picking_hero_scene
        self.challenge_complete_scene = challenge_complete_scene
        self.game_state = game_state
        self.ui_state = ui_state
        self.game_engine = game_engine
        self.total_time_played: Millis = 0
        self.init_flags = init_flags

    def on_startup(self, new_hero_was_created: bool):
        self.ui_state.set_message("Challenge starting...")
        if new_hero_was_created:
            self.game_state.player_state.modify_money(100)
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
            return SceneTransition(self.picking_hero_scene(self.init_flags))
        elif event == EngineEvent.ENEMY_DIED:
            num_enemies = len([npc for npc in self.game_state.non_player_characters if npc.is_enemy])
            if num_enemies == 0:
                return SceneTransition(self.challenge_complete_scene(self.total_time_played))
            self.ui_state.set_message(str(num_enemies) + " enemies remaining")
        return None
