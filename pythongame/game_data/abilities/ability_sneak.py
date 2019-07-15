from typing import Optional

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Event, BuffEventOutcome

SNEAKING_DURATION = Millis(10000)
DAMAGE_BONUS_DURATION = Millis(1500)
SNEAKING_SPEED_DECREASE = 0.5
SNEAKING_BUFF = BuffType.SNEAKING
AFTER_SNEAKING_BUFF = BuffType.AFTER_SNEAKING
SNEAKING_ABILITY_TYPE = AbilityType.SNEAK
DAMAGE_BONUS = 1


# TODO Make all enemies consider invis correctly

# TODO Should there be a charge-up time for using invis, to stop it from being used mid-combat as a pure damage bonus?

def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(SNEAKING_BUFF), SNEAKING_DURATION)
    return True


class Sneaking(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True
        # TODO Wearing items that grant movement speed are too effective at countering this
        game_state.player_entity.add_to_speed_multiplier(-SNEAKING_SPEED_DECREASE)
        game_state.player_state.damage_modifier_bonus += DAMAGE_BONUS

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False
        game_state.player_entity.add_to_speed_multiplier(SNEAKING_SPEED_DECREASE)
        game_state.player_state.gain_buff_effect(get_buff_effect(AFTER_SNEAKING_BUFF), DAMAGE_BONUS_DURATION)

    def get_buff_type(self):
        return SNEAKING_BUFF

    def buff_handle_event(self, notification: Event) -> Optional[BuffEventOutcome]:
        used_other_ability = notification.player_used_ability \
                             and notification.player_used_ability != SNEAKING_ABILITY_TYPE
        player_lost_health = notification.player_lost_health
        if used_other_ability or player_lost_health:
            return BuffEventOutcome.cancel_effect()


# TODO add defensive element to this effect (chance to dodge attacks for example)
class AfterSneaking(AbstractBuffEffect):

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BONUS

    def get_buff_type(self):
        return AFTER_SNEAKING_BUFF


def register_sneak_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_SNEAK

    register_ability_effect(SNEAKING_ABILITY_TYPE, _apply_ability)
    description = "Sneaks up on enemies (+" + str(DAMAGE_BONUS * 100) + "% dmg for " \
                  + "{:.1f}".format(DAMAGE_BONUS_DURATION / 1000) + "s)"
    ability_data = AbilityData("Sneak", ui_icon_sprite, 10, Millis(10000), description, None)
    register_ability_data(SNEAKING_ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/sneak_icon.png")
    register_buff_effect(SNEAKING_BUFF, Sneaking)
    register_buff_text(SNEAKING_BUFF, "Sneaking")
    register_buff_effect(AFTER_SNEAKING_BUFF, AfterSneaking)
    register_buff_text(AFTER_SNEAKING_BUFF, "Element of surprise")
