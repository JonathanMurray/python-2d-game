from typing import Optional

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Event, BuffEventOutcome, \
    PlayerUsedAbilityEvent, PlayerLostHealthEvent

ABILITY_TYPE = AbilityType.SNEAK
BUFF_SNEAK = BuffType.SNEAKING
BUFF_POST_SNEAK = BuffType.AFTER_SNEAKING
DURATION_SNEAK = Millis(10000)
DURATION_POST_SNEAK = Millis(2500)
SPEED_DECREASE = 0.5
DAMAGE_BONUS = 1
ARMOR_BONUS = 5


# TODO Should there be a charge-up time for using invis, to stop it from being used mid-combat as a pure damage bonus?

def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_SNEAK), DURATION_SNEAK)
    return True


class Sneaking(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True
        # TODO Wearing items that grant movement speed are too effective at countering this
        game_state.player_entity.add_to_speed_multiplier(-SPEED_DECREASE)
        game_state.player_state.damage_modifier_bonus += DAMAGE_BONUS
        game_state.player_state.armor += ARMOR_BONUS

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False
        game_state.player_entity.add_to_speed_multiplier(SPEED_DECREASE)
        game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_POST_SNEAK), DURATION_POST_SNEAK)

    def get_buff_type(self):
        return BUFF_SNEAK

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        used_other_ability = isinstance(event, PlayerUsedAbilityEvent) and event.ability != ABILITY_TYPE
        player_lost_health = isinstance(event, PlayerLostHealthEvent)
        if used_other_ability or player_lost_health:
            return BuffEventOutcome.cancel_effect()


class AfterSneaking(AbstractBuffEffect):

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BONUS
        game_state.player_state.armor -= ARMOR_BONUS

    def get_buff_type(self):
        return BUFF_POST_SNEAK


def register_sneak_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_SNEAK

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Invis -> [+" + str(DAMAGE_BONUS * 100) + "% dmg, +" + str(ARMOR_BONUS) + " armor for " \
                  + "{:.1f}".format(DURATION_POST_SNEAK / 1000) + "s]"
    ability_data = AbilityData("Sneak", ui_icon_sprite, 10, Millis(10000), description, None)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/sneak_icon.png")
    register_buff_effect(BUFF_SNEAK, Sneaking)
    register_buff_text(BUFF_SNEAK, "Sneaking")
    register_buff_effect(BUFF_POST_SNEAK, AfterSneaking)
    register_buff_text(BUFF_POST_SNEAK, "Element of surprise")
