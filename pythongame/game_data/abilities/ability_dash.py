from typing import Optional

from pygame.rect import Rect

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully, \
    AbilityFailedToExecute
from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import AbilityType, Millis, UiIconSprite, SoundId, BuffType, HeroUpgradeId, HeroStat, \
    PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_buff_text
from pythongame.core.game_state import GameState, NonPlayerCharacter, CameraShake
from pythongame.core.math import translate_in_direction
from pythongame.core.visual_effects import VisualCircle, VisualRect, VisualLine
from pythongame.core.world_entity import WorldEntity

ABILITY_TYPE = AbilityType.DASH
BUFF_FROM_STEALTH = BuffType.AFTER_DASH
BUFF_FROM_STEALTH_DURATION = Millis(7_000)
BUFF_SPEED = BuffType.SPEED_BUFF_FROM_DASH
BUFF_SPEED_DURATION = Millis(2000)
DAMAGE = 5
FROM_STEALTH_DODGE_CHANCE_BOOST = 0.1
FROM_STEALTH_LIFE_STEAL_BOOST = 0.15
FROM_STEALTH_MAGIC_RESIST_CHANCE_BOOST = 0.2


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    previous_position = player_entity.get_center_position()

    used_from_stealth = game_state.player_state.has_active_buff(BuffType.STEALTHING)

    for distance in range(40, 200, 10):
        new_position = translate_in_direction((player_entity.x, player_entity.y), player_entity.direction,
                                              distance)
        if game_state.game_world.is_position_within_game_world(new_position) \
                and not game_state.game_world.would_entity_collide_if_new_pos(player_entity, new_position):
            if _would_collide_with_wall(game_state, player_entity, distance):
                return AbilityFailedToExecute(reason="Wall is blocking")
            should_regain_mana_and_cd = False
            enemy_hit = _get_enemy_that_was_hit(game_state, player_entity, distance)
            if enemy_hit:
                game_state.camera_shake = CameraShake(Millis(50), Millis(150), 4)
                deal_player_damage_to_enemy(game_state, enemy_hit, DAMAGE, DamageType.MAGIC)
                has_reset_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_DASH_KILL_RESET)
                enemy_died = enemy_hit.health_resource.is_at_or_below_zero()
                if has_reset_upgrade and enemy_died:
                    should_regain_mana_and_cd = True

            player_entity.set_position(new_position)
            new_center_position = player_entity.get_center_position()
            color = (250, 140, 80)
            game_state.game_world.visual_effects.append(VisualCircle(color, previous_position, 17, 35, Millis(150), 1))
            game_state.game_world.visual_effects.append(
                VisualLine(color, previous_position, new_center_position, Millis(250), 2))
            game_state.game_world.visual_effects.append(VisualRect(color, previous_position, 37, 46, Millis(150), 1))
            game_state.game_world.visual_effects.append(
                VisualCircle(color, new_center_position, 25, 40, Millis(300), 1, player_entity))
            has_speed_upgrade = game_state.player_state.has_upgrade(HeroUpgradeId.ABILITY_DASH_MOVEMENT_SPEED)
            if has_speed_upgrade:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_SPEED), BUFF_SPEED_DURATION)
            if used_from_stealth:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_FROM_STEALTH), BUFF_FROM_STEALTH_DURATION)
            return AbilityWasUsedSuccessfully(should_regain_mana_and_cd=should_regain_mana_and_cd)
    return AbilityFailedToExecute(reason="No space")


def _get_enemy_that_was_hit(game_state: GameState, player_entity: WorldEntity, distance_jumped: int) \
        -> Optional[NonPlayerCharacter]:
    previous_position = (player_entity.x, player_entity.y)
    partial_distance = 10
    while partial_distance < distance_jumped:
        intermediate_position = translate_in_direction(previous_position, player_entity.direction, partial_distance)
        enemies_hit = game_state.game_world.get_enemy_intersecting_rect(
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
        intersection = game_state.game_world.walls_state.does_rect_intersect_with_wall(
            (intermediate_position[0], intermediate_position[1], player_entity.pygame_collision_rect.w,
             player_entity.pygame_collision_rect.h))
        if intersection:
            return True
        partial_distance += 10
    return False


class FromStealth(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_FROM_STEALTH,
                         {HeroStat.DODGE_CHANCE: FROM_STEALTH_DODGE_CHANCE_BOOST,
                          HeroStat.LIFE_STEAL: FROM_STEALTH_LIFE_STEAL_BOOST,
                          HeroStat.MAGIC_RESIST_CHANCE: FROM_STEALTH_MAGIC_RESIST_CHANCE_BOOST})


class IncreasedSpeedAfterDash(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_SPEED, {HeroStat.MOVEMENT_SPEED: 0.4})
        self.timer = PeriodicTimer(Millis(100))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.game_world.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.game_world.player_entity.get_center_position(), 5, 10,
                             Millis(200), 0))


def register_dash_ability():
    ui_icon_sprite = UiIconSprite.ABILITY_DASH
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    description = "Dash over an enemy, dealing " + str(DAMAGE) + " magic damage. [from stealth: gain " + \
                  "+{:.0f}".format(FROM_STEALTH_DODGE_CHANCE_BOOST * 100) + "% dodge chance, " + \
                  "+{:.0f}".format(FROM_STEALTH_LIFE_STEAL_BOOST * 100) + "% life steal, " + \
                  "+{:.0f}".format(FROM_STEALTH_MAGIC_RESIST_CHANCE_BOOST * 100) + "% magic resist for " + \
                  "{:.0f}".format(BUFF_FROM_STEALTH_DURATION / 1000) + "s]"
    mana_cost = 12
    ability_data = AbilityData("Dash", ui_icon_sprite, mana_cost, Millis(4000), description, SoundId.ABILITY_DASH)
    register_ability_data(ABILITY_TYPE, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/icon_ability_dash.png")
    register_buff_effect(BUFF_FROM_STEALTH, FromStealth)
    register_buff_text(BUFF_FROM_STEALTH, "Element of surprise")
    register_buff_effect(BUFF_SPEED, IncreasedSpeedAfterDash)
