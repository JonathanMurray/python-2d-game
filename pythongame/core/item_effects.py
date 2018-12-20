from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState


class AbstractItemEffect:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass

    def get_item_type(self):
        pass


_item_effects: Dict[ItemType, AbstractItemEffect] = {}


def register_item_effect(item_type: ItemType, effect: AbstractItemEffect):
    _item_effects[item_type] = effect


def get_item_effect(item_type: ItemType) -> AbstractItemEffect:
    return _item_effects[item_type]
