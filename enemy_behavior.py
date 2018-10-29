import random

from common import *
from game_data import ENEMY_PROJECTILE_SIZE
from game_state import WorldEntity, Projectile


def create_enemy_mind(enemy_behavior):
    if enemy_behavior == EnemyBehavior.DUMB:
        return DumbEnemyMind()
    elif enemy_behavior == EnemyBehavior.SMART:
        return SmartEnemyMind()
    else:
        raise Exception("Unhandled behavior: " + str(enemy_behavior))


class DumbEnemyMind:
    def __init__(self):
        self._time_since_run = 0
        self._run_interval = 750

    def control_enemy(self, game_state, enemy_world_entity, player_entity, is_player_invisible, time_passed):
        self._time_since_run += time_passed
        if self._time_since_run > self._run_interval:
            self._time_since_run = 0
            if is_player_invisible:
                direction = random_direction()
            else:
                direction = _get_direction_between(enemy_world_entity, player_entity)
                if random.random() < 0.2:
                    direction = random.choice(_get_perpendicular_directions(direction))
            enemy_world_entity.set_moving_in_dir(direction)


class SmartEnemyMind:
    def __init__(self):
        self._time_since_run = 0
        self._run_interval = 350
        self._time_since_firing = 0
        self._update_firing_cooldown()
        self._pause_after_fire_duration = 700

    def control_enemy(self, game_state, enemy_world_entity, player_entity, is_player_invisible, time_passed):
        self._time_since_firing += time_passed
        self._time_since_run += time_passed
        if self._time_since_run > self._run_interval \
                and self._time_since_firing > self._pause_after_fire_duration:
            self._time_since_run = 0
            if is_player_invisible:
                direction = random_direction()
                enemy_world_entity.set_moving_in_dir(direction)
            else:
                if self._time_since_firing > self._firing_cooldown:
                    self._time_since_firing = 0
                    self._update_firing_cooldown()
                    enemy_world_entity.set_not_moving()
                    center_position = enemy_world_entity.get_center_position()
                    projectile_pos = (center_position[0] - ENEMY_PROJECTILE_SIZE[0] / 2,
                                      center_position[1] - ENEMY_PROJECTILE_SIZE[1] / 2)
                    entity = WorldEntity(projectile_pos, ENEMY_PROJECTILE_SIZE, Sprite.POISONBALL,
                                         enemy_world_entity.direction, 2)
                    game_state.projectile_entities.append(Projectile(entity, 0, 2000, False))
                else:
                    direction = _get_direction_between(enemy_world_entity, player_entity)
                    enemy_world_entity.set_moving_in_dir(direction)

    def _update_firing_cooldown(self):
        self._firing_cooldown = 1500 + random.random() * 5000


def _get_direction_between(from_entity, to_entity):
    dx = to_entity.x - from_entity.x
    dy = to_entity.y - from_entity.y
    if abs(dx) > abs(dy):
        if dx > 0:
            direction = Direction.RIGHT
        else:
            direction = Direction.LEFT
    else:
        if dy < 0:
            direction = Direction.UP
        else:
            direction = Direction.DOWN
    return direction


def _get_perpendicular_directions(direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]
