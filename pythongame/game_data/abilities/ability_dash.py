from typing import Optional

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.buff_effects import register_buff_effect, AbstractBuffEffect, get_buff_effect
from pythongame.core.common import AbilityType, Millis, UiIconSprite, SoundId, BuffType
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualCircle, VisualRect, VisualLine

BUFF_DURATION = Millis(3000)

ABILITY_TYPE = AbilityType.DASH
BUFF_TYPE = BuffType.AFTER_DASH
ARMOR_BOOST = 1


def _apply_ability(game_state: GameState) -> bool:
    player_entity = game_state.player_entity
    previous_position = player_entity.get_center_position()

    for distance in [40, 50, 60, 70, 80, 90, 100, 110, 120, 130]:
        new_position = translate_in_direction((player_entity.x, player_entity.y), player_entity.direction,
                                              distance)
        is_valid_pos = not game_state.would_entity_collide_if_new_pos(player_entity, new_position)
        if is_valid_pos:
            if _would_collide_with_wall(game_state, player_entity, distance):
                return False
            enemy_hit = _get_enemy_that_was_hit(game_state, player_entity, distance)
            if enemy_hit:
                damage = 5
                deal_player_damage_to_enemy(game_state, enemy_hit, damage)
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)
            player_entity.set_position(new_position)
            new_center_position = player_entity.get_center_position()
            color = (250, 140, 80)
            game_state.visual_effects.append(VisualCircle(color, previous_position, 17, 35, Millis(150), 1))
            game_state.visual_effects.append(VisualLine(color, previous_position, new_center_position, Millis(250), 2))
            game_state.visual_effects.append(VisualRect(color, previous_position, 37, 46, Millis(150), 1))
            game_state.visual_effects.append(
                VisualCircle(color, new_center_position, 25, 40, Millis(300), 1, player_entity))
            return True
    return False


def _get_enemy_that_was_hit(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) \
        -> Optional[NonPlayerCharacter]:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        enemies_hit = game_state.get_enemy_intersecting_rect(
            (intermediate_position[0], intermediate_position[1], player_entity.w, player_entity.h))
        if enemies_hit:
            return enemies_hit[0]
        partial_distance += 10
    return None


def _would_collide_with_wall(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) -> bool:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        intersection = game_state.does_rect_intersect_with_wall(
            (intermediate_position[0], intermediate_position[1], player_entity.w, player_entity.h))
        if intersection:
            return True
        partial_distance += 10
    return False


class AfterDash(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.armor += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.armor -= ARMOR_BOOST

    def get_buff_type(self):
        return BUFF_TYPE


def register_dash_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_DASH
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Dash forward, gain armor if enemy was hit"
    ability_data = AbilityData("Dash", ui_icon_sprite, 5, Millis(4000), description, SoundId.ABILITY_DASH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_ability_dash.png")
    register_buff_effect(BUFF_TYPE, AfterDash)
    register_buff_text(BUFF_TYPE, "Increased armor")
