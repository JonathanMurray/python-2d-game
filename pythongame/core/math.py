import random
from typing import Tuple, List

from pygame.rect import Rect

from pythongame.core.common import Direction


def rect_from_corners(corner1: Tuple[int, int], corner2: Tuple[int, int]):
    x_values = [corner1[0], corner2[0]]
    y_values = [corner1[1], corner2[1]]
    x0 = min(x_values)
    y0 = min(y_values)
    w = max(x_values) - x0
    h = max(y_values) - y0
    return Rect(x0, y0, w, h)


# deprecated - only used by view
def is_point_in_rect(point: Tuple[int, int], rect: Rect):
    return rect.collidepoint(point[0], point[1])


def boxes_intersect(r1: Rect, r2: Rect):
    return r1.colliderect(r2)


def rects_intersect(r1: Rect, r2: Rect):
    return r1.colliderect(r2)


def random_direction():
    return random.choice([Direction.LEFT, Direction.RIGHT, Direction.UP, Direction.DOWN])


# Returns 2 directions, starting with vertical or horizontal depending on which is closer to the true direction
# Example: (0, 0) -> (2, 1) gives [RIGHT, DOWN]
# Example: (0, 0) -> (2, 0) gives [RIGHT, None]
# noinspection PyShadowingNames
def get_directions_to_position(from_entity, position) -> Tuple[Direction, Direction]:
    dx = position[0] - from_entity.x
    dy = position[1] - from_entity.y
    dir_from_dx = lambda dx: Direction.RIGHT if dx > 0 else (Direction.LEFT if dx < 0 else None)
    dir_from_dy = lambda dy: Direction.UP if dy < 0 else (Direction.DOWN if dy > 0 else None)
    if abs(dx) > abs(dy):
        return dir_from_dx(dx), dir_from_dy(dy)
    else:
        return dir_from_dy(dy), dir_from_dx(dx)


def get_perpendicular_directions(direction: Direction) -> List[Direction]:
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


def get_opposite_direction(direction: Direction) -> Direction:
    if direction == direction.LEFT:
        return direction.RIGHT
    if direction == direction.RIGHT:
        return direction.LEFT
    if direction == direction.UP:
        return direction.DOWN
    if direction == direction.DOWN:
        return direction.UP


def get_position_from_center_position(center_position: Tuple[int, int], size: Tuple[int, int]):
    return center_position[0] - size[0] / 2, center_position[1] - size[1] / 2


def translate_in_direction(position: Tuple[int, int], direction: Direction, amount: int) -> Tuple[int, int]:
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


# TODO use Vector2
def sum_of_vectors(v1: Tuple[int, int], v2: Tuple[int, int]) -> Tuple[int, int]:
    return v1[0] + v2[0], v1[1] + v2[1]


# TODO use Vector2
def is_x_and_y_within_distance(a: Tuple[int, int], b: Tuple[int, int], distance: int):
    return abs(a[0] - b[0]) < distance and abs(a[1] - b[1]) < distance


# TODO use Vector2
def get_manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# TODO use Vector2
def get_manhattan_distance_between_rects(a: Rect, b: Rect) -> int:
    a_left = a[0]
    a_right = a[0] + a[2]
    a_top = a[1]
    a_bot = a[1] + a[3]
    b_left = b[0]
    b_right = b[0] + b[2]
    b_top = b[1]
    b_bot = b[1] + b[3]
    if a_right < b_left:
        hor_dinstance = b_left - a_right  # a is left of b
    elif a_left < b_right:
        hor_dinstance = 0  # a overlaps horizontally with b
    else:
        hor_dinstance = a_left - b_right  # a is right of b
    if a_bot < b_top:
        ver_distance = b_top - a_bot  # a is over b
    elif a_top < b_bot:
        ver_distance = 0  # a overlaps vertically with b
    else:
        ver_distance = a_top - b_bot  # a is under b
    return hor_dinstance + ver_distance


def get_rect_with_increased_size_in_all_directions(rect, increased_amount):
    return (rect[0] - increased_amount, rect[1] - increased_amount, rect[2] + increased_amount * 2,
            rect[3] + increased_amount * 2)


# TODO use Vector2
def get_middle_point(pos_1: Tuple[int, int], pos_2: Tuple[int, int]) -> Tuple[int, int]:
    return int((pos_1[0] + pos_2[0]) / 2), int((pos_1[1] + pos_2[1]) / 2)


def get_relative_pos_within_rect(point: Tuple[int, int], rect: Rect) -> Tuple[float, float]:
    return (point[0] - rect.x) / rect.w, (point[1] - rect.y) / rect.h
