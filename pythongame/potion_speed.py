from pythongame.buffs import AbstractBuff, register_buff_effect
from pythongame.common import PotionType, BuffType, Millis
from pythongame.game_data import register_ui_icon_sprite_path, UiIconSprite, register_potion_icon_sprite, \
    register_buff_text
from pythongame.game_state import GameState
from pythongame.potions import create_potion_visual_effect_at_player, PotionWasConsumed, register_potion_effect
from pythongame.visual_effects import VisualCircle


def _apply_speed(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff(BuffType.INCREASED_MOVE_SPEED, Millis(3500))
    return PotionWasConsumed()


class IncreasedMoveSpeed(AbstractBuff):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(1)

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 100:
            game_state.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.player_entity.get_center_position(), 10, Millis(200), 0))
            self._time_since_graphics = 0

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-1)


def register_speed_potion():
    register_potion_effect(PotionType.SPEED, _apply_speed)
    register_buff_effect(BuffType.INCREASED_MOVE_SPEED, IncreasedMoveSpeed())
    register_buff_text(BuffType.INCREASED_MOVE_SPEED, "Speed")
    register_potion_icon_sprite(PotionType.SPEED, UiIconSprite.SPEED_POTION)
    register_ui_icon_sprite_path(UiIconSprite.SPEED_POTION, "resources/white_potion.gif")
