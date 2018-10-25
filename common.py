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


class PotionType(Enum):
    HEALTH = 1
    MANA = 2
