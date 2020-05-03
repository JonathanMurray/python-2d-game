import math

from pythongame.core.common import *


class HealthOrManaResource:
    def __init__(self, max_value: int, regen: float):
        self._value_float = max_value
        self.value = max_value
        self.max_value = max_value
        self.base_regen = regen
        self.regen_bonus = 0
        self.value_was_updated = Observable()

    def gain(self, amount: float) -> int:
        value_before = self.value
        self._value_float = min(self._value_float + amount, self.max_value)
        self.value = int(math.floor(self._value_float))
        amount_gained = self.value - value_before
        self._notify_observers()
        return amount_gained

    def lose(self, amount: float) -> int:
        value_before = self.value
        self._value_float = min(self._value_float - amount, self.max_value)
        self.value = int(math.floor(self._value_float))
        amount_lost = value_before - self.value
        self._notify_observers()
        return amount_lost

    def set_zero(self):
        self._value_float = 0
        self.value = 0
        self._notify_observers()

    def gain_to_max(self) -> int:
        value_before = self.value
        self._value_float = self.max_value
        self.value = self.max_value
        amount_gained = self.value - value_before
        self._notify_observers()
        return amount_gained

    def set_to_partial_of_max(self, partial: float):
        self._value_float = partial * self.max_value
        self.value = int(math.floor(self._value_float))
        self._notify_observers()

    def regenerate(self, time_passed: Millis):
        self.gain(self.get_effective_regen() / 1000.0 * float(time_passed))

    def is_at_max(self):
        return self.value == self.max_value

    def is_at_or_below_zero(self):
        return self.value <= 0

    def increase_max(self, amount: int):
        self.max_value += amount

    def decrease_max(self, amount: int):
        self.max_value -= amount
        if self.value > self.max_value:
            self._value_float = self.max_value
            self.value = int(math.floor(self._value_float))
            self._notify_observers()

    def get_partial(self) -> float:
        return self.value / self.max_value

    def get_effective_regen(self) -> float:
        return self.base_regen + self.regen_bonus

    def _notify_observers(self):
        self.value_was_updated.notify((self.value, self.max_value))
