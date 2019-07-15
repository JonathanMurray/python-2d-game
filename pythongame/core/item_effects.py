from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState, Event


class AbstractItemEffect:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass

    def get_item_type(self):
        pass

    def item_handle_event(self, notification: Event):
        pass


_item_effects: Dict[ItemType, AbstractItemEffect] = {}


def register_item_effect(item_type: ItemType, effect: AbstractItemEffect):
    _item_effects[item_type] = effect


# Note this is handled differently compared to buffs
# There is only one effect instance per item type - having duplicate items with active effects may not be well supported
def get_item_effect(item_type: ItemType) -> AbstractItemEffect:
    return _item_effects[item_type]
