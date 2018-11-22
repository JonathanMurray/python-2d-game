import random
from enum import Enum

from typing import NewType, Tuple

Millis = NewType('Millis', int)


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def _ranges_overlap(a_min: int, a_max: int, b_min: int, b_max: int):
    return (a_min <= b_max) and (b_min <= a_max)


def boxes_intersect(r1, r2):
    return _ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
           and _ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)


def rects_intersect(r1, r2):
    return _ranges_overlap(r1[0], r1[0] + r1[2], r2[0], r2[0] + r2[2]) \
           and _ranges_overlap(r1[1], r1[1] + r1[3], r2[1], r2[1] + r2[3])


def random_direction():
    return random.choice([Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN])


def get_direction_between(from_entity, to_entity):
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


# Returns 2 directions, starting with vertical or horizontal depending on which is closer to the true direction
# Example: (0, 0) -> (2, 1) gives [RIGHT, DOWN]
def get_directions_to_position(from_entity, position):
    dx = position[0] - from_entity.x
    dy = position[1] - from_entity.y
    dir_from_dx = lambda dx: Direction.RIGHT if dx > 0 else (Direction.LEFT if dx < 0 else None)
    dir_from_dy = lambda dy: Direction.UP if dy < 0 else (Direction.DOWN if dy > 0 else None)
    if abs(dx) > abs(dy):
        return dir_from_dx(dx), dir_from_dy(dy)
    else:
        return dir_from_dy(dy), dir_from_dx(dx)


def get_perpendicular_directions(direction: Direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


def get_opposite_direction(direction: Direction):
    if direction == direction.LEFT:
        return direction.RIGHT
    if direction == direction.RIGHT:
        return direction.LEFT
    if direction == direction.UP:
        return direction.DOWN
    if direction == direction.DOWN:
        return direction.UP


def get_all_directions():
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


def get_position_from_center_position(center_position: Tuple[int, int], size: Tuple[int, int]):
    return center_position[0] - size[0] / 2, center_position[1] - size[1] / 2


def translate_in_direction(position: Tuple[int, int], direction: Direction, amount: int):
    if direction == Direction.RIGHT:
        return position[0] + amount, position[1]
    elif direction == Direction.DOWN:
        return position[0], position[1] + amount
    elif direction == Direction.LEFT:
        return position[0] - amount, position[1]
    elif direction == Direction.UP:
        return position[0], position[1] - amount
    else:
        raise Exception("Unhandled direction: " + str(direction))


def is_x_and_y_within_distance(a: Tuple[int, int], b: Tuple[int, int], distance: int):
    return abs(a[0] - b[0]) < distance and abs(a[1] - b[1]) < distance


def get_rect_with_increased_size_in_all_directions(rect, increased_amount):
    return (rect[0] - increased_amount, rect[1] - increased_amount, rect[2] + increased_amount * 2,
            rect[3] + increased_amount * 2)


class PotionType(Enum):
    HEALTH = 1
    MANA = 2
    SPEED = 3
    INVISIBILITY = 4


class EnemyType(Enum):
    DUMB = 1
    SMART = 2
    MAGE = 3
    BERSERKER = 4
    RAT_1 = 5
    RAT_2 = 6


class AbilityType(Enum):
    HEAL = 1
    FIREBALL = 2
    AOE_ATTACK = 3
    CHANNEL_ATTACK = 4
    TELEPORT = 5


class Sprite(Enum):
    PLAYER = 1
    ENEMY = 2
    ENEMY_2 = 3
    PROJECTILE_PLAYER_FIREBALL = 4
    WHIRLWIND = 5
    HEALTH_POTION = 6
    POISONBALL = 7
    ENEMY_MAGE = 8
    ENEMY_BERSERKER = 9
    MAGIC_MISSILE = 10
    WALL = 11
    RAT_1 = 12
    RAT_2 = 13


class BuffType(Enum):
    HEALING_OVER_TIME = 1
    DAMAGE_OVER_TIME = 2
    INCREASED_MOVE_SPEED = 3
    INVISIBILITY = 4
    CHANNELING_MAGIC_MISSILES = 5


class ProjectileType(Enum):
    PLAYER_FIREBALL = 1
    PLAYER_AOE = 2
    ENEMY_POISON = 3
    PLAYER_MAGIC_MISSILE = 4
