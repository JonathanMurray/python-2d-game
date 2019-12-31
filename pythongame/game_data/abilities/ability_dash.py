from typing import Optional

from pygame.rect import Rect

from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully, \
    AbilityFailedToExecute
from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import AbilityType, Millis, UiIconSprite, SoundId, BuffType, HeroUpgrade, HeroStat, \
    PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ability_data, AbilityData, register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, CameraShake
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualCircle, VisualRect, VisualLine

ABILITY_TYPE = AbilityType.DASH
BUFF_AFTER_ENEMY_JUMP = BuffType.AFTER_DASH
BUFF_AFTER_ENEMY_JUMP_DURATION = Millis(3000)
BUFF_SPEED = BuffType.SPEED_BUFF_FROM_DASH
BUFF_SPEED_DURATION = Millis(2000)
HEALTH_REGEN_BOOST = 5
DAMAGE = 5
DODGE_CHANCE_BOOST = 0.05


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.player_entity
    previous_position = player_entity.get_center_position()

    for distance in range(40, 200, 10):
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
                deal_player_damage_to_enemy(game_state, enemy_hit, DAMAGE, DamageType.MAGIC)
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_AFTER_ENEMY_JUMP),
                                                         BUFF_AFTER_ENEMY_JUMP_DURATION)
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
            has_speed_upgrade = game_state.player_state.has_upgrade(HeroUpgrade.ABILITY_DASH_MOVEMENT_SPEED)
            if has_speed_upgrade:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_SPEED), BUFF_SPEED_DURATION)
            return AbilityWasUsedSuccessfully(should_regain_mana_and_cd=should_regain_mana_and_cd)
    return AbilityFailedToExecute(reason="No space")


def _get_enemy_that_was_hit(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) \
        -> Optional[NonPlayerCharacter]:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        enemies_hit = game_state.get_enemy_intersecting_rect(
            Rect(intermediate_position[0], intermediate_position[1], player_entity.pygame_collision_rect.w,
                 player_entity.pygame_collision_rect.h))
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
            (intermediate_position[0], intermediate_position[1], player_entity.pygame_collision_rect.w,
             player_entity.pygame_collision_rect.h))
        if intersection:
            return True
        partial_distance += 10
    return False


class AfterEnemyJump(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_AFTER_ENEMY_JUMP,
                         {HeroStat.DODGE_CHANCE: DODGE_CHANCE_BOOST, HeroStat.HEALTH_REGEN: HEALTH_REGEN_BOOST})


class IncreasedSpeedAfterDash(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_SPEED, {HeroStat.MOVEMENT_SPEED: 0.4})
        self.timer = PeriodicTimer(Millis(100))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.player_entity.get_center_position(), 5, 10, Millis(200), 0))


def register_dash_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_DASH
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Dash over an enemy, dealing " + str(DAMAGE) + " magic damage. Then, gain +" + \
                  "{:.0f}".format(DODGE_CHANCE_BOOST * 100) + "% dodge chance and +" + \
                  str(HEALTH_REGEN_BOOST) + " health regen"
    mana_cost = 12
    ability_data = AbilityData("Dash", ui_icon_sprite, mana_cost, Millis(4000), description, SoundId.ABILITY_DASH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_ability_dash.png")
    register_buff_effect(BUFF_AFTER_ENEMY_JUMP, AfterEnemyJump)
    register_buff_text(BUFF_AFTER_ENEMY_JUMP, "Protected")
    register_buff_effect(BUFF_SPEED, IncreasedSpeedAfterDash)
