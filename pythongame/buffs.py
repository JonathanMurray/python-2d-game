from typing import Dict

from pythongame.common import *
from pythongame.game_state import GameState


class AbstractBuff:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass


_buff_effects: Dict[BuffType, AbstractBuff] = {}


def register_buff_effect(buff_type: BuffType, effect: AbstractBuff):
    _buff_effects[buff_type] = effect


def get_buff_effect(buff_type: BuffType) -> AbstractBuff:
    return _buff_effects[buff_type]
