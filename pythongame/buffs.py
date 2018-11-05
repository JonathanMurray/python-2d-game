from pythongame.common import *
from pythongame.game_state import GameState


class AbstractBuff:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass


BUFF_EFFECTS = {}


def register_buff_effect(buff_type: BuffType, effect: AbstractBuff):
    BUFF_EFFECTS[buff_type] = effect
