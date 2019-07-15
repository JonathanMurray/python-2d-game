from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ConsumableType, BuffType, Millis
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite, register_buff_text, ConsumableData, \
    register_consumable_data, ConsumableCategory
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.visual_effects import VisualRect

BUFF_TYPE = BuffType.INVISIBILITY
POTION_TYPE = ConsumableType.INVISIBILITY


def _apply_invis(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INVISIBILITY), Millis(5000))
    return ConsumableWasConsumed()


class Invisibility(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 320:
            self._time_since_graphics = 0
            game_state.visual_effects.append(
                VisualRect((0, 0, 250), game_state.player_entity.get_center_position(), 45, 60, Millis(400),
                           1, game_state.player_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False

    def get_buff_type(self):
        return BUFF_TYPE


def register_invis_potion():
    register_consumable_effect(POTION_TYPE, _apply_invis)
    register_buff_effect(BUFF_TYPE, Invisibility)
    register_buff_text(BUFF_TYPE, "Invisibility")
    register_ui_icon_sprite_path(UiIconSprite.POTION_INVISIBILITY, "resources/graphics/invis_potion.png")
    data = ConsumableData(UiIconSprite.POTION_INVISIBILITY, None, "Invisibility potion",
                          "Grants temporary invisibility", ConsumableCategory.OTHER)
    register_consumable_data(POTION_TYPE, data)
