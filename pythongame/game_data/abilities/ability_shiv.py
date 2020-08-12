import random

from pygame.rect import Rect

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully
from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PLAYER_ENTITY_SIZE, \
    HeroUpgradeId
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path
from pythongame.core.game_state import GameState, CameraShake
from pythongame.core.math import translate_in_direction
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualRect, VisualCross

MIN_DMG = 3
MAX_DMG = 5

SHIV_STEALTH_DAMAGE_MULTIPLIER = 3.5
SHIV_UPGRADED_STEALTH_DAMAGE_MULTIPLIER = 4

SHIV_TALENT_FULL_HEALTH_DAMAGE_MULTIPLIER = 1.5


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    rect_w = 28
    slash_center_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + PLAYER_ENTITY_SIZE[0] * 0.25)

    slash_rect = Rect(int(slash_center_pos[0] - rect_w / 2), int(slash_center_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.game_world.get_enemy_intersecting_rect(slash_rect)
    is_stealthed = game_state.player_state.has_active_buff(BuffType.STEALTHING)
    if is_stealthed:
        play_sound(SoundId.ABILITY_SHIV_STEALTHED)
    else:
        play_sound(SoundId.ABILITY_SHIV)
    for enemy in affected_enemies:
        damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)

        # Note: Dependency on other ability 'stealth'
        if is_stealthed:
            # Talent: increase the damage bonus that Shiv gets from being used while stealthing
            has_damage_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_SHIV_SNEAK_BONUS_DAMAGE)
            damage *= SHIV_UPGRADED_STEALTH_DAMAGE_MULTIPLIER if has_damage_upgrade else SHIV_STEALTH_DAMAGE_MULTIPLIER
            game_state.camera_shake = CameraShake(Millis(50), Millis(150), 4)
        else:
            # Talent: if attacking an enemy that's at 100% health while not stealthing, deal bonus damage
            has_damage_upgrade = game_state.player_state.has_upgrade(
                HeroUpgradeId.ABILITY_SHIV_FULL_HEALTH_BONUS_DAMAGE)
            if has_damage_upgrade and enemy.health_resource.is_at_max():
                damage *= SHIV_TALENT_FULL_HEALTH_DAMAGE_MULTIPLIER

        deal_player_damage_to_enemy(game_state, enemy, damage, DamageType.PHYSICAL, visual_emphasis=is_stealthed)
        break

    game_state.game_world.visual_effects.append(
        VisualRect((150, 150, 75), slash_center_pos, rect_w, int(rect_w * 0.7), Millis(200), 2, None))
    game_state.game_world.visual_effects.append(VisualCross((100, 100, 70), slash_center_pos, 6, Millis(100), 2))

    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(250))
    return AbilityWasUsedSuccessfully()


def register_shiv_ability():
    ability_type = AbilityType.SHIV
    ui_icon_sprite = UiIconSprite.ABILITY_SHIV

    register_ability_effect(ability_type, _apply_ability)
    description = "Deal " + str(MIN_DMG) + "-" + str(MAX_DMG) + " physical damage to one enemy in front of you. " + \
                  "[from stealth: 350% damage]"
    ability_data = AbilityData("Shiv", ui_icon_sprite, 1, Millis(400), description, None)
    register_ability_data(ability_type, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/double_edged_dagger.png")
