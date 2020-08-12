from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, AbilityType, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.visual_effects import create_visual_healing_text, VisualCircle
from pythongame.core.world_entity import WorldEntity


def _apply_heal(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.HEALING_OVER_TIME), Millis(3500))
    return AbilityWasUsedSuccessfully()


class HealingOverTime(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        healing_amount = 0.04
        game_state.player_state.health_resource.gain(healing_amount * float(time_passed))
        if self._time_since_graphics > 500:
            estimate_health_gained = int(self._time_since_graphics * healing_amount)
            game_state.game_world.visual_effects.append(
                create_visual_healing_text(game_state.game_world.player_entity, estimate_health_gained))
            game_state.game_world.visual_effects.append(
                VisualCircle((200, 200, 50), game_state.game_world.player_entity.get_center_position(),
                             5, 10, Millis(100), 0))
            self._time_since_graphics = 0

    def get_buff_type(self):
        return BuffType.HEALING_OVER_TIME


def register_heal_ability():
    register_ability_effect(AbilityType.HEAL, _apply_heal)
    register_ability_data(
        AbilityType.HEAL,
        AbilityData("Heal", UiIconSprite.ABILITY_HEAL, 10, Millis(15000), "TODO", None))
    register_ui_icon_sprite_path(UiIconSprite.ABILITY_HEAL, "resources/graphics/heal_ability.png")
    register_buff_effect(BuffType.HEALING_OVER_TIME, HealingOverTime)
    register_buff_text(BuffType.HEALING_OVER_TIME, "Healing")
