import random

from pygame.rect import Rect

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, UiIconSprite, SoundId, PLAYER_ENTITY_SIZE, HeroUpgrade
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path
from pythongame.core.game_state import GameState
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualRect, VisualCross

MIN_DMG = 3
MAX_DMG = 4


def _apply_ability(game_state: GameState) -> bool:
    player_entity = game_state.player_entity
    rect_w = 28
    slash_center_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + PLAYER_ENTITY_SIZE[0] * 0.25)

    slash_rect = Rect(int(slash_center_pos[0] - rect_w / 2), int(slash_center_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.get_enemy_intersecting_rect(slash_rect)
    for enemy in affected_enemies:
        damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)

        # Note: Dependency on other ability 'sneak'
        if game_state.player_state.has_active_buff(BuffType.SNEAKING):
            has_damage_upgrade = game_state.player_state.has_upgrade(HeroUpgrade.ABILITY_SHIV_SNEAK_BONUS_DAMAGE)
            damage *= 4 if has_damage_upgrade else 3.5

        deal_player_damage_to_enemy(game_state, enemy, damage)
        break

    game_state.visual_effects.append(
        VisualRect((150, 150, 75), slash_center_pos, rect_w, int(rect_w * 0.7), Millis(200), 2, None))
    game_state.visual_effects.append(VisualCross((100, 100, 70), slash_center_pos, 6, Millis(100), 2))

    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(250))
    return True


def register_shiv_ability():
    ability_type = AbilityType.SHIV
    ui_icon_sprite = UiIconSprite.ABILITY_SHIV

    register_ability_effect(ability_type, _apply_ability)
    description = "Deal " + str(MIN_DMG) + "-" + str(MAX_DMG) + " damage to one enemy in front of you. " + \
                  "[from stealth: 350% damage]"
    ability_data = AbilityData("Shiv", ui_icon_sprite, 1, Millis(400), description, SoundId.ABILITY_SHIV)
    register_ability_data(ability_type, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/double_edged_dagger.png")
