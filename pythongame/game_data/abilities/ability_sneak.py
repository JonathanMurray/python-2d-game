from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter

# TODO Wearing items that grant movement speed are too effective at countering this
SNEAKING_SPEED_DECREASE = 0.5
BUFF_TYPE = BuffType.SNEAKING


def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), Millis(10000))
    return True


class Sneaking(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True
        game_state.player_entity.add_to_speed_multiplier(-SNEAKING_SPEED_DECREASE)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 320:
            self._time_since_graphics = 0

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False
        game_state.player_entity.add_to_speed_multiplier(SNEAKING_SPEED_DECREASE)

    def get_buff_type(self):
        return BUFF_TYPE


def register_sneak_ability():
    ability_type = AbilityType.SNEAK
    ui_icon_sprite = UiIconSprite.ABILITY_SNEAK

    register_ability_effect(ability_type, _apply_ability)
    description = "Sneaks, hiding from enemies"
    register_ability_data(
        ability_type,
        AbilityData("Sneak", ui_icon_sprite, 10, Millis(5000), description, None))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/double_edged_dagger.png")
    register_buff_effect(BUFF_TYPE, Sneaking)
    register_buff_text(BUFF_TYPE, "Sneaking")
