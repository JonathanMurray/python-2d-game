import random
from common import Direction


def _get_perpendicular_directions(direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


def run_ai_for_enemy_against_target(enemy_world_entity, target_entity):
    dx = target_entity.x - enemy_world_entity.x
    dy = target_entity.y - enemy_world_entity.y
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
    if random.random() < 0.2:
        direction = random.choice(_get_perpendicular_directions(direction))
    return direction
