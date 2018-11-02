from typing import Tuple

from pythongame.common import Millis


class VisualEffect:
    def __init__(self, max_age):
        self.age = 0
        self.max_age = max_age
        self.has_expired = False

    def notify_time_passed(self, time_passed: Millis):
        self.age += time_passed
        if self.age > self.max_age:
            self.has_expired = True


class VisualLine(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], start_position: Tuple[int, int], end_position: Tuple[int, int],
                 max_age: Millis):
        super().__init__(max_age)
        self.color = color
        self.start_position = start_position
        self.end_position = end_position


class VisualCircle(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], center_position: Tuple[int, int], radius: int, max_age: Millis):
        super().__init__(max_age)
        self.color = color
        self.center_position = center_position
        self.start_radius = int(radius / 2)
        self.end_radius = radius


class VisualRect(VisualEffect):
    def __init__(self, color: Tuple[int, int, int], center_position: Tuple[int, int], width: int, max_age: Millis):
        super().__init__(max_age)
        self.color = color
        self.center_position = center_position
        self.start_width = int(width * 0.75)
        self.end_width = width
