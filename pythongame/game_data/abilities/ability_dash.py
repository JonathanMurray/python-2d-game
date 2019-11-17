from typing import Optional

from pygame.rect import Rect

from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully, \
    AbilityFailedToExecute
from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import AbilityType, Millis, UiIconSprite, SoundId, BuffType, HeroUpgrade, HeroStat
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, CameraShake
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualCircle, VisualRect, VisualLine

BUFF_DURATION = Millis(3000)

ABILITY_TYPE = AbilityType.DASH
BUFF_TYPE = BuffType.AFTER_DASH
HEALTH_REGEN_BOOST = 5
DAMAGE = 5
DODGE_CHANCE_BOOST = 0.05


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.player_entity
    previous_position = player_entity.get_center_position()

    for distance in [40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]:
        new_position = translate_in_direction((player_entity.x, player_entity.y), player_entity.direction,
                                              distance)
        if game_state.is_position_within_game_world(new_position) \
                and not game_state.would_entity_collide_if_new_pos(player_entity, new_position):
            if _would_collide_with_wall(game_state, player_entity, distance):
                return AbilityFailedToExecute(reason="Wall is blocking")
            should_regain_mana_and_cd = False
            enemy_hit = _get_enemy_that_was_hit(game_state, player_entity, distance)
            if enemy_hit:
                game_state.camera_shake = CameraShake(Millis(50), Millis(150), 4)
                deal_player_damage_to_enemy(game_state, enemy_hit, DAMAGE)
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)
                has_reset_upgrade = game_state.player_state.has_upgrade(HeroUpgrade.ABILITY_DASH_KILL_RESET)
                enemy_died = enemy_hit.health_resource.is_at_or_below_zero()
                if has_reset_upgrade and enemy_died:
                    should_regain_mana_and_cd = True

            player_entity.set_position(new_position)
            new_center_position = player_entity.get_center_position()
            color = (250, 140, 80)
            game_state.visual_effects.append(VisualCircle(color, previous_position, 17, 35, Millis(150), 1))
            game_state.visual_effects.append(VisualLine(color, previous_position, new_center_position, Millis(250), 2))
            game_state.visual_effects.append(VisualRect(color, previous_position, 37, 46, Millis(150), 1))
            game_state.visual_effects.append(
                VisualCircle(color, new_center_position, 25, 40, Millis(300), 1, player_entity))
            return AbilityWasUsedSuccessfully(should_regain_mana_and_cd=should_regain_mana_and_cd)
    return AbilityFailedToExecute(reason="No space")


def _get_enemy_that_was_hit(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) \
        -> Optional[NonPlayerCharacter]:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        enemies_hit = game_state.get_enemy_intersecting_rect(
            Rect(intermediate_position[0], intermediate_position[1], player_entity.w, player_entity.h))
        if enemies_hit:
            return enemies_hit[0]
        partial_distance += 10
    return None


def _would_collide_with_wall(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) -> bool:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        intersection = game_state.walls_state.does_rect_intersect_with_wall(
            (intermediate_position[0], intermediate_position[1], player_entity.w, player_entity.h))
        if intersection:
            return True
        partial_distance += 10
    return False


class AfterDash(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE,
                         {HeroStat.DODGE_CHANCE: DODGE_CHANCE_BOOST, HeroStat.HEALTH_REGEN: HEALTH_REGEN_BOOST})


def register_dash_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_DASH
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Dash over an enemy, dealing " + str(DAMAGE) + " damage. Then, gain +" + \
                  "{:.0f}".format(DODGE_CHANCE_BOOST * 100) + "% dodge chance and +" + \
                  str(HEALTH_REGEN_BOOST) + " health regen"
    mana_cost = 12
    ability_data = AbilityData("Dash", ui_icon_sprite, mana_cost, Millis(4000), description, SoundId.ABILITY_DASH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_ability_dash.png")
    register_buff_effect(BUFF_TYPE, AfterDash)
    register_buff_text(BUFF_TYPE, "Protected")
