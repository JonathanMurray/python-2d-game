from typing import Optional

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PeriodicTimer
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Event, BuffEventOutcome, \
    PlayerUsedAbilityEvent, PlayerLostHealthEvent
from pythongame.core.visual_effects import VisualCircle

ABILITY_TYPE = AbilityType.SNEAK
BUFF_SNEAK = BuffType.SNEAKING
BUFF_POST_SNEAK = BuffType.AFTER_SNEAKING
DURATION_SNEAK = Millis(15000)
DURATION_POST_SNEAK = Millis(2500)
SPEED_DECREASE = 0.3
ARMOR_BONUS = 5


def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_SNEAK), DURATION_SNEAK)
    return True


class Sneaking(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True
        game_state.player_entity.add_to_speed_multiplier(-SPEED_DECREASE)
        game_state.player_state.armor_bonus += ARMOR_BONUS

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False
        game_state.player_entity.add_to_speed_multiplier(SPEED_DECREASE)
        game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_POST_SNEAK), DURATION_POST_SNEAK)

    def get_buff_type(self):
        return BUFF_SNEAK

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        used_shiv_ability = isinstance(event, PlayerUsedAbilityEvent) and event.ability == AbilityType.SHIV
        player_lost_health = isinstance(event, PlayerLostHealthEvent)
        if used_shiv_ability or player_lost_health:
            return BuffEventOutcome.cancel_effect()


class AfterSneaking(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(160))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            visual_effect = VisualCircle(
                (250, 150, 250), buffed_entity.get_center_position(), 18, 25, Millis(220), 1, buffed_entity)
            game_state.visual_effects.append(visual_effect)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.armor_bonus -= ARMOR_BONUS

    def get_buff_type(self):
        return BUFF_POST_SNEAK


def register_sneak_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_SNEAK

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Become invisible. Shiv deals 300% damage from stealth. Then, gain " + \
                  str(ARMOR_BONUS) + " armor for " + "{:.1f}".format(DURATION_POST_SNEAK / 1000) + "s"
    mana_cost = 20
    ability_data = AbilityData("Sneak", ui_icon_sprite, mana_cost, Millis(10000), description, SoundId.ABILITY_SNEAK)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/sneak_icon.png")
    register_buff_effect(BUFF_SNEAK, Sneaking)
    register_buff_text(BUFF_SNEAK, "Sneaking")
    register_buff_effect(BUFF_POST_SNEAK, AfterSneaking)
    register_buff_text(BUFF_POST_SNEAK, "Element of surprise")
