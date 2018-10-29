import random

from common import *


def _get_perpendicular_directions(direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


def create_enemy_mind(enemy_behavior):
    return EnemyMind(enemy_behavior)


class EnemyMind:
    def __init__(self, enemy_behavior):
        self.enemy_behavior = enemy_behavior

    def control_enemy(self, enemy_world_entity, player_entity, is_player_invisible):
        if is_player_invisible:
            direction = random_direction()
        else:
            dx = player_entity.x - enemy_world_entity.x
            dy = player_entity.y - enemy_world_entity.y
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
            if self.enemy_behavior == EnemyBehavior.DUMB:
                if random.random() < 0.2:
                    direction = random.choice(_get_perpendicular_directions(direction))
        enemy_world_entity.set_moving_in_dir(direction)
