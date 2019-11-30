from typing import Optional

from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PeriodicTimer, HeroUpgrade, \
    HeroStat
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text, ABILITIES
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Event, BuffEventOutcome, \
    PlayerUsedAbilityEvent, PlayerLostHealthEvent
from pythongame.core.hero_upgrades import register_hero_upgrade_effect
from pythongame.core.visual_effects import VisualCircle

ABILITY_TYPE = AbilityType.STEALTH
BUFF_STEALTH = BuffType.STEALTHING
BUFF_POST_STEALTH = BuffType.AFTER_STEALTHING
DURATION_STEALTH = Millis(15000)
DURATION_POST_STEALTH = Millis(2500)
SPEED_DECREASE = 0.3
DODGE_CHANCE_BONUS = 0.05


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.force_cancel_all_buffs()
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_STEALTH), DURATION_STEALTH)
    return AbilityWasUsedSuccessfully()


class Stealthing(StatModifyingBuffEffect):

    def __init__(self):
        super().__init__(BUFF_STEALTH,
                         {HeroStat.MOVEMENT_SPEED: -SPEED_DECREASE, HeroStat.DODGE_CHANCE: DODGE_CHANCE_BONUS})

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        super().apply_start_effect(game_state, buffed_entity, buffed_npc)
        game_state.player_state.is_invisible = True

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        super().apply_end_effect(game_state, buffed_entity, buffed_npc)
        game_state.player_state.is_invisible = False

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        used_ability = isinstance(event, PlayerUsedAbilityEvent) and event.ability != AbilityType.STEALTH
        player_lost_health = isinstance(event, PlayerLostHealthEvent)
        if used_ability or player_lost_health:
            return BuffEventOutcome.cancel_effect()


class AfterStealthing(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(160))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            visual_effect = VisualCircle(
                (250, 150, 250), buffed_entity.get_center_position(), 18, 25, Millis(220), 1, buffed_entity)
            game_state.visual_effects.append(visual_effect)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.modify_stat(HeroStat.DODGE_CHANCE, -DODGE_CHANCE_BONUS)

    def get_buff_type(self):
        return BUFF_POST_STEALTH


def _upgrade_mana_cost(_game_state: GameState):
    ABILITIES[ABILITY_TYPE].mana_cost = 20


def register_stealth_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_STEALTH

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Become invisible to enemies. After effect ends, gain +" + \
                  "{:.0f}".format(DODGE_CHANCE_BONUS * 100) + "% dodge chance for " + \
                  "{:.1f}".format(DURATION_POST_STEALTH / 1000) + "s"
    mana_cost = 25
    cooldown = Millis(6000)
    ability_data = AbilityData("Stealth", ui_icon_sprite, mana_cost, cooldown, description, SoundId.ABILITY_STEALTH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/sneak_icon.png")
    register_buff_effect(BUFF_STEALTH, Stealthing)
    register_buff_text(BUFF_STEALTH, "Stealthed")
    register_buff_effect(BUFF_POST_STEALTH, AfterStealthing)
    register_buff_text(BUFF_POST_STEALTH, "Element of surprise")
    register_hero_upgrade_effect(HeroUpgrade.ABILITY_STEALTH_MANA_COST, _upgrade_mana_cost)
