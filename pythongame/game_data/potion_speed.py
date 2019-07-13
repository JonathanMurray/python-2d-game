from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ConsumableType, BuffType, Millis, UiIconSprite
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_ui_icon_sprite_path, register_buff_text, \
    register_consumable_data, ConsumableData
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.visual_effects import VisualCircle


def _apply_speed(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INCREASED_MOVE_SPEED), Millis(3500))
    return ConsumableWasConsumed()


class IncreasedMoveSpeed(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_entity.add_to_speed_multiplier(1)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 100:
            game_state.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.player_entity.get_center_position(), 5, 10, Millis(200), 0))
            self._time_since_graphics = 0

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_entity.add_to_speed_multiplier(-1)

    def get_buff_type(self):
        return BuffType.INCREASED_MOVE_SPEED


def register_speed_potion():
    register_consumable_effect(ConsumableType.SPEED, _apply_speed)
    register_buff_effect(BuffType.INCREASED_MOVE_SPEED, IncreasedMoveSpeed)
    register_buff_text(BuffType.INCREASED_MOVE_SPEED, "Speed")
    register_ui_icon_sprite_path(UiIconSprite.POTION_SPEED, "resources/graphics/white_potion.gif")
    register_consumable_data(
        ConsumableType.SPEED,
        ConsumableData(UiIconSprite.POTION_SPEED, None, "Speed potion", "Grants temporarily increased movement speed"))
