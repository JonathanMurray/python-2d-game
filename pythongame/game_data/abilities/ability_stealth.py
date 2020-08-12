from typing import Optional

from pythongame.core.abilities import AbilityData, ABILITIES, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, HeroUpgradeId, \
    HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, NonPlayerCharacter, Event, BuffEventOutcome, \
    PlayerUsedAbilityEvent, PlayerLostHealthEvent
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, AbstractHeroUpgradeEffect
from pythongame.core.world_entity import WorldEntity

STEALTH_MANA_COST = 25
STEALTH_UPGRADED_MANA_COST = 20

STEALTH_COOLDOWN = Millis(5000)

ABILITY_TYPE = AbilityType.STEALTH
BUFF_STEALTH = BuffType.STEALTHING
DURATION_STEALTH = Millis(10000)
MOVEMENT_SPEED_DECREASE = 0.3


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.force_cancel_all_buffs()
    has_speed_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_STEALTH_MOVEMENT_SPEED)
    speed_decrease = MOVEMENT_SPEED_DECREASE if not has_speed_upgrade else 0
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_STEALTH, speed_decrease), DURATION_STEALTH)
    return AbilityWasUsedSuccessfully()


class Stealthing(StatModifyingBuffEffect):

    def __init__(self, movement_speed_decrease: float):
        super().__init__(BUFF_STEALTH, {HeroStat.MOVEMENT_SPEED: -movement_speed_decrease})

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


class UpgradeStealthManaCost(AbstractHeroUpgradeEffect):
    def apply(self, game_state: GameState):
        ABILITIES[ABILITY_TYPE].mana_cost = STEALTH_UPGRADED_MANA_COST

    def revert(self, game_state: GameState):
        ABILITIES[ABILITY_TYPE].mana_cost = STEALTH_MANA_COST


def register_stealth_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_STEALTH

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Become invisible to enemies, and add effects to your other abilities."
    ability_data = AbilityData("Stealth", ui_icon_sprite, STEALTH_MANA_COST, STEALTH_COOLDOWN, description,
                               SoundId.ABILITY_STEALTH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/sneak_icon.png")
    register_buff_effect(BUFF_STEALTH, Stealthing)
    register_buff_text(BUFF_STEALTH, "Stealthed")
    register_hero_upgrade_effect(HeroUpgradeId.ABILITY_STEALTH_MANA_COST, UpgradeStealthManaCost())
