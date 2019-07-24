import random

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import AbilityType, Millis, BuffType, HeroId, UiIconSprite
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    HEROES
from pythongame.core.game_state import GameState
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualRect

MIN_DMG = 2
MAX_DMG = 4


def _apply_ability(game_state: GameState) -> bool:
    player_entity = game_state.player_entity
    rect_w = 36
    # Note: We assume that this ability is used by this specific hero
    hero_entity_size = HEROES[HeroId.WARRIOR].entity_size
    slash_pos = translate_in_direction(
        player_entity.get_center_position(),
        player_entity.direction,
        rect_w / 2 + hero_entity_size[0] * 0.25)

    slash_rect = (int(slash_pos[0] - rect_w / 2), int(slash_pos[1] - rect_w / 2), rect_w, rect_w)
    affected_enemies = game_state.get_enemy_intersecting_rect(slash_rect)
    for enemy in affected_enemies:
        damage: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
        deal_player_damage_to_enemy(game_state, enemy, damage)

    game_state.visual_effects.append(
        VisualRect((100, 0, 0), slash_pos, rect_w, int(rect_w * 0.7), Millis(200), 2, None))
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.RECOVERING_AFTER_ABILITY), Millis(300))
    return True


def register_sword_slash_ability():
    ability_type = AbilityType.SWORD_SLASH
    ui_icon_sprite = UiIconSprite.ABILITY_SWORD_SLASH

    register_ability_effect(ability_type, _apply_ability)
    description = "Deal " + str(MIN_DMG) + "-" + str(MAX_DMG) + " damage to enemies in front of you."
    register_ability_data(
        ability_type,
        AbilityData("Slash", ui_icon_sprite, 0, Millis(700), description, None))
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_slash.png")
