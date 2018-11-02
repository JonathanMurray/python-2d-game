import random
from enum import Enum

from typing import NewType

Millis = NewType('Millis', int)


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def ranges_overlap(a_min: int, a_max: int, b_min: int, b_max: int):
    return (a_min <= b_max) and (b_min <= a_max)


def boxes_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
           and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)


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


class PotionType(Enum):
    HEALTH = 1
    MANA = 2
    SPEED = 3
    INVISIBILITY = 4


class EnemyBehavior(Enum):
    DUMB = 1
    SMART = 2
    MAGE = 3
    BERSERKER = 4


class AbilityType(Enum):
    HEAL = 1
    ATTACK = 2
    AOE_ATTACK = 3
    CHANNEL_ATTACK = 4


class Sprite(Enum):
    PLAYER = 1
    ENEMY = 2
    ENEMY_2 = 3
    FIREBALL = 4
    WHIRLWIND = 5
    HEALTH_POTION = 6
    POISONBALL = 7
    ENEMY_MAGE = 8
    ENEMY_BERSERKER = 9
    MAGIC_MISSILE = 10


class BuffType(Enum):
    HEALING_OVER_TIME = 1
    DAMAGE_OVER_TIME = 2
    INCREASED_MOVE_SPEED = 3
    INVISIBILITY = 4
    CHANNELING_MAGIC_MISSILES = 5


class ProjectileType(Enum):
    PLAYER = 1
    PLAYER_AOE = 2
    ENEMY_POISON = 3
    PLAYER_MAGIC_MISSILE = 4
