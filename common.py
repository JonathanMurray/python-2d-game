import random
from enum import Enum


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def _ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)


def boxes_intersect(r1, r2):
    return _ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
           and _ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)


def random_direction():
    return random.choice([Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN])


class PotionType(Enum):
    HEALTH = 1
    MANA = 2
    SPEED = 3
    INVISIBILITY = 4


class EnemyBehavior(Enum):
    DUMB = 1
    SMART = 2


class AbilityType(Enum):
    HEAL = 1
    ATTACK = 2
    AOE_ATTACK = 3


class Sprite(Enum):
    PLAYER = 1
    ENEMY = 2
    ENEMY_2 = 3
    FIREBALL = 4
    WHIRLWIND = 5


class UiIconSprite(Enum):
    HEALTH_POTION = 1
    MANA_POTION = 2
    SPEED_POTION = 3
    ATTACK_ABILITY = 4
    HEAL_ABILITY = 5
    AOE_ABILITY = 6
    INVISIBILITY_POTION = 7


class BuffType(Enum):
    HEALING_OVER_TIME = 1
    DAMAGE_OVER_TIME = 2
    INCREASED_MOVE_SPEED = 3
    INVISIBILITY = 4
