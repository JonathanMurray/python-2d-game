from typing import Optional

from pythongame.core.abilities import AbilityData, ABILITIES, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully
from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import BuffType, Millis, AbilityType, UiIconSprite, SoundId, PeriodicTimer, HeroUpgradeId, \
    HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, NonPlayerCharacter, Event, BuffEventOutcome, \
    EnemyDiedEvent
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, AbstractHeroUpgradeEffect
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity

COOLDOWN = Millis(25000)
BUFF_DURATION = Millis(15000)
BUFF_TYPE = BuffType.BLOOD_LUST
LIFE_STEAL_BONUS_RATIO = 0.15
SPEED_BONUS = 0.3
BLOODLUST_INCREASED_DURATION_FROM_KILL = Millis(1000)
BLOODLUST_UPGRADED_INCREASED_DURATION_FROM_KILL = Millis(1500)
SWORD_SLASH_CD_BONUS = Millis(100)

# This variable is updated when picking the talent
has_blood_lust_duration_increase_upgrade = False


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)
    return AbilityWasUsedSuccessfully()


class BloodLust(StatModifyingBuffEffect):

    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.LIFE_STEAL: LIFE_STEAL_BONUS_RATIO, HeroStat.MOVEMENT_SPEED: SPEED_BONUS})
        self.timer = PeriodicTimer(Millis(250))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        super().apply_start_effect(game_state, buffed_entity, buffed_npc)
        sword_slash_data = ABILITIES[AbilityType.SWORD_SLASH]
        sword_slash_data.cooldown -= SWORD_SLASH_CD_BONUS

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            visual_effect = VisualCircle(
                (250, 0, 0,), buffed_entity.get_center_position(), 25, 30, Millis(350), 1, buffed_entity)
            game_state.game_world.visual_effects.append(visual_effect)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        super().apply_end_effect(game_state, buffed_entity, buffed_npc)
        sword_slash_data = ABILITIES[AbilityType.SWORD_SLASH]
        sword_slash_data.cooldown += SWORD_SLASH_CD_BONUS

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        if isinstance(event, EnemyDiedEvent):
            if has_blood_lust_duration_increase_upgrade:
                duration_increase = BLOODLUST_UPGRADED_INCREASED_DURATION_FROM_KILL
            else:
                duration_increase = BLOODLUST_INCREASED_DURATION_FROM_KILL
            return BuffEventOutcome.change_remaining_duration(duration_increase)


class UpgradeBloodlust(AbstractHeroUpgradeEffect):
    def apply(self, game_state: GameState):
        global has_blood_lust_duration_increase_upgrade
        has_blood_lust_duration_increase_upgrade = True

    def revert(self, game_state: GameState):
        global has_blood_lust_duration_increase_upgrade
        has_blood_lust_duration_increase_upgrade = False


def register_bloodlust_ability():
    ability_type = AbilityType.BLOOD_LUST
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ABILITY_BLOODLUST
    description = "Gain Bloodlust for " + "{:.0f}".format(BUFF_DURATION / 1000) + "s " + \
                  "(+" + str(int(LIFE_STEAL_BONUS_RATIO * 100)) + "% lifesteal, " + \
                  "reduced Slash cooldown, " + \
                  "+" + str(int(SPEED_BONUS * 100)) + "% movement speed). " + \
                  "Duration is increased by " + "{:.0f}".format(BLOODLUST_INCREASED_DURATION_FROM_KILL / 1000) + \
                  "s for each enemy killed."
    register_ability_data(
        ability_type,
        AbilityData("Bloodlust", ui_icon_sprite, 25, COOLDOWN, description, SoundId.ABILITY_BLOODLUST))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_bloodlust.png")
    register_buff_effect(BUFF_TYPE, BloodLust)
    register_buff_text(BUFF_TYPE, "Bloodlust")
    register_hero_upgrade_effect(HeroUpgradeId.ABILITY_BLOODLUST_DURATION, UpgradeBloodlust())
