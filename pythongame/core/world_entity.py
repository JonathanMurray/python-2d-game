from typing import Tuple, Optional

from pygame.rect import Rect

from pythongame.core.common import Sprite, Direction, Observable, Millis
from pythongame.core.math import translate_in_direction


class WorldEntity:
    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int], sprite: Sprite, direction=Direction.LEFT, speed=0):
        self.x: int = pos[0]
        self.y: int = pos[1]
        self.sprite: Sprite = sprite
        self.direction: Direction = direction
        self._speed = speed
        self._speed_multiplier = 1  # update and get using methods
        self._effective_speed = speed
        self._is_moving = True
        self.pygame_collision_rect: Rect = Rect(self.x, self.y, size[0], size[1])
        self.movement_animation_progress: float = 0  # goes from 0 to 1 repeatedly
        self.visible = True  # Should only be used to control rendering
        self.view_z = 0  # increasing Z values = moving into the screen
        self.movement_changed: Observable = None  # space optimization: Only allocate when needed (i.e. for player entity)
        self.position_changed: Observable = None  # space optimization: Only allocate when needed (i.e. for player entity)

    def set_moving_in_dir(self, direction: Direction):
        if direction is None:
            raise Exception("Need to provide a valid direciton to move in")
        self.direction = direction
        if not self._is_moving:
            self.notify_movement_observers(True)
        self._is_moving = True

    def set_not_moving(self):
        if self._is_moving:
            self.notify_movement_observers(False)
        self._is_moving = False

    def notify_movement_observers(self, is_moving: bool):
        if self.movement_changed is not None:
            self.movement_changed.notify(is_moving)

    def notify_position_observers(self):
        if self.position_changed is not None:
            self.position_changed.notify(self.get_center_position())

    def get_new_position_according_to_dir_and_speed(self, time_passed: Millis) -> Optional[Tuple[int, int]]:
        distance = self._effective_speed * time_passed
        if self._is_moving:
            return translate_in_direction((self.x, self.y), self.direction, distance)
        return None

    def update_movement_animation(self, time_passed: Millis):
        if self._is_moving:
            self.update_animation(time_passed)

    def update_animation(self, time_passed):
        self.movement_animation_progress = (self.movement_animation_progress + float(time_passed) / 700) % 1

    def get_new_position_according_to_other_dir_and_speed(self, direction: Direction, time_passed: Millis) \
            -> Optional[Tuple[int, int]]:
        distance = self._effective_speed * time_passed
        return translate_in_direction((self.x, self.y), direction, distance)

    def get_center_position(self) -> Tuple[int, int]:
        return self.pygame_collision_rect.center

    def get_position(self) -> Tuple[int, int]:
        return int(self.x), int(self.y)

    def add_to_speed_multiplier(self, amount: float):
        self._speed_multiplier += amount
        self._effective_speed = self._speed_multiplier * self._speed

    def set_speed_multiplier(self, multiplier: float):
        # Only call this method as part of setup
        self._speed_multiplier = multiplier
        self._effective_speed = self._speed_multiplier * self._speed

    def get_speed_multiplier(self):
        return self._speed_multiplier

    # TODO use more
    def rect(self) -> Rect:
        return self.pygame_collision_rect

    def set_position(self, new_position: Tuple[int, int]):
        self.x = new_position[0]
        self.y = new_position[1]
        self.pygame_collision_rect.x = self.x
        self.pygame_collision_rect.y = self.y
        self.notify_position_observers()

    def rotate_right(self):
        dirs = {
            Direction.DOWN: Direction.LEFT,
            Direction.LEFT: Direction.UP,
            Direction.UP: Direction.RIGHT,
            Direction.RIGHT: Direction.DOWN
        }
        self.direction = dirs[self.direction]

    def rotate_left(self):
        dirs = {
            Direction.DOWN: Direction.RIGHT,
            Direction.RIGHT: Direction.UP,
            Direction.UP: Direction.LEFT,
            Direction.LEFT: Direction.DOWN
        }
        self.direction = dirs[self.direction]
