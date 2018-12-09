from pythongame.core.buffs import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import PotionType, BuffType, Millis
from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite, register_potion_icon_sprite, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, Enemy
from pythongame.core.potions import create_potion_visual_effect_at_player, PotionWasConsumed, register_potion_effect
from pythongame.core.visual_effects import VisualRect


def _apply_invis(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INVISIBILITY), Millis(5000))
    return PotionWasConsumed()


class Invisibility(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        game_state.player_state.is_invisible = True

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 320:
            self._time_since_graphics = 0
            game_state.visual_effects.append(
                VisualRect((0, 0, 250), game_state.player_entity.get_center_position(), 45, 60, Millis(400),
                           1, game_state.player_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        game_state.player_state.is_invisible = False

    def get_buff_type(self):
        return BuffType.INVISIBILITY


def register_invis_potion():
    register_potion_effect(PotionType.INVISIBILITY, _apply_invis)
    register_buff_effect(BuffType.INVISIBILITY, Invisibility)
    register_buff_text(BuffType.INVISIBILITY, "Invisibility")
    register_potion_icon_sprite(PotionType.INVISIBILITY, UiIconSprite.INVISIBILITY_POTION)
    register_ui_icon_sprite_path(UiIconSprite.INVISIBILITY_POTION, "resources/graphics/invis_potion.png")
