from typing import Optional

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text, register_buff_as_channeling
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Event, PlayerUsedAbilityEvent, \
    BuffEventOutcome

ABILITY_TYPE = AbilityType.INFUSE_DAGGER
BUFF_CHANNELING = BuffType.CHANNELING_INFUSE_DAGGER
BUFF_INFUSED = BuffType.HAS_INFUSED_DAGGER
DEBUFF_SPEED_DECREASE = 0.5
DEBUFF = BuffType.DAMAGED_BY_INFUSED_DAGGER


def _apply_ability(game_state: GameState) -> bool:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_CHANNELING), Millis(2000))
    return True


class ChannelingInfuseDagger(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.add_stun()
        game_state.player_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.remove_stun()
        game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_INFUSED), Millis(60000))

    def get_buff_type(self):
        return BUFF_CHANNELING


class HasInfusedDagger(AbstractBuffEffect):
    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        if isinstance(event, PlayerUsedAbilityEvent):
            if event.ability == AbilityType.SHIV:
                return BuffEventOutcome.cancel_effect()

    def get_buff_type(self):
        return BUFF_INFUSED


class DamagedByInfusedDagger(AbstractBuffEffect):

    def __init__(self):
        self.time_since_damage = 0

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(-DEBUFF_SPEED_DECREASE)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self.time_since_damage += time_passed
        if self.time_since_damage > 750:
            self.time_since_damage = 0
            deal_player_damage_to_enemy(game_state, buffed_npc, 1)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(DEBUFF_SPEED_DECREASE)

    def get_buff_type(self):
        return DEBUFF


def register_infuse_dagger_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_INFUSE_DAGGER

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "On next Shiv: slow, damage-over-time"
    ability_data = AbilityData("Infuse Dagger", ui_icon_sprite, 25, Millis(20000), description, None)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/ability_infuse_dagger.png")
    register_buff_effect(BUFF_CHANNELING, ChannelingInfuseDagger)
    register_buff_as_channeling(BUFF_CHANNELING)

    register_buff_effect(BUFF_INFUSED, HasInfusedDagger)
    register_buff_text(BUFF_INFUSED, "Infused dagger")

    register_buff_effect(DEBUFF, DamagedByInfusedDagger)
