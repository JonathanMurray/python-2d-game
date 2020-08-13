import random

from pygame.rect import Rect

from pythongame.core.abilities import AbilityData, ABILITIES, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, HeroId, UiIconSprite, SoundId, HeroUpgradeId
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    HEROES
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, AbstractHeroUpgradeEffect
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualRect

ABILITY_TYPE = AbilityType.SWORD_SLASH
ABILITY_SLASH_COOLDOWN = Millis(700)
ABILITY_SLASH_UPGRADED_COOLDOWN = Millis(600)

MIN_DMG = 2
MAX_DMG = 5


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    rect_w = 36
    # Note: We assume that this ability is used by this specific hero
    hero_entity_size = HEROES[HeroId.WARRIOR].entity_size
    slash_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + hero_entity_size[0] * 0.25)

    slash_rect = Rect(int(slash_pos[0] - rect_w / 2), int(slash_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.game_world.get_enemy_intersecting_rect(slash_rect)
    has_aoe_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_SLASH_AOE_BONUS_DAMAGE)
    hit_multiple_enemies = len(affected_enemies) > 1
    for enemy in affected_enemies:
        if has_aoe_upgrade and hit_multiple_enemies:
            damage: float = MAX_DMG
        else:
            damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
        deal_player_damage_to_enemy(game_state, enemy, damage, DamageType.PHYSICAL)

    game_state.game_world.visual_effects.append(
        VisualRect((100, 0, 0), slash_pos, rect_w, int(rect_w * 0.7), Millis(200), 2, None))
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(300))
    return AbilityWasUsedSuccessfully()


class UpgradeSwordSlashCooldown(AbstractHeroUpgradeEffect):
    def apply(self, game_state: GameState):
        ABILITIES[ABILITY_TYPE].cooldown = ABILITY_SLASH_UPGRADED_COOLDOWN

    def revert(self, game_state: GameState):
        ABILITIES[ABILITY_TYPE].cooldown = ABILITY_SLASH_COOLDOWN


def register_sword_slash_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_SWORD_SLASH

    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Deal " + str(MIN_DMG) + "-" + str(MAX_DMG) + " physical damage to enemies in front of you."
    register_ability_data(
        ABILITY_TYPE,
        AbilityData("Slash", ui_icon_sprite, 1, ABILITY_SLASH_COOLDOWN, description, SoundId.ABILITY_SLASH))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_slash.png")
    register_hero_upgrade_effect(HeroUpgradeId.ABILITY_SLASH_CD, UpgradeSwordSlashCooldown())
