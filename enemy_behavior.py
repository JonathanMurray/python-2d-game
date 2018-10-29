import random

from common import *
from game_data import ATTACK_PROJECTILE_SIZE
from game_state import WorldEntity, Projectile


def create_enemy_mind(enemy_behavior):
    if enemy_behavior == EnemyBehavior.DUMB:
        return DumbEnemyMind()
    elif enemy_behavior == EnemyBehavior.SMART:
        return SmartEnemyMind()
    else:
        raise Exception("Unhandled behavior: " + str(enemy_behavior))


class DumbEnemyMind:
    def control_enemy(self, game_state, enemy_world_entity, player_entity, is_player_invisible, time_passed):
        if is_player_invisible:
            direction = random_direction()
        else:
            direction = _get_direction_between(enemy_world_entity, player_entity)
            if random.random() < 0.2:
                direction = random.choice(_get_perpendicular_directions(direction))
        enemy_world_entity.set_moving_in_dir(direction)


class SmartEnemyMind:
    def __init__(self):
        self._time_since_action = 0

    def control_enemy(self, game_state, enemy_world_entity, player_entity, is_player_invisible, time_passed):
        self._time_since_action += time_passed
        if self._time_since_action > 3000:
            enemy_world_entity.set_not_moving()
            center_position = enemy_world_entity.get_center_position()
            projectile_pos = (center_position[0] - ATTACK_PROJECTILE_SIZE[0] / 2,
                              center_position[1] - ATTACK_PROJECTILE_SIZE[1] / 2)
            entity = WorldEntity(projectile_pos, ATTACK_PROJECTILE_SIZE, Sprite.FIREBALL,
                                 enemy_world_entity.direction, 2.5)
            game_state.projectile_entities.append(Projectile(entity, 0, 3000, False))
            self._time_since_action = 0
        else:
            if is_player_invisible:
                direction = random_direction()
            else:
                direction = _get_direction_between(enemy_world_entity, player_entity)
            enemy_world_entity.set_moving_in_dir(direction)


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
