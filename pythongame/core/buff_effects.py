from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import GameState, WorldEntity, Enemy


class AbstractBuffEffect:
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        pass

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy):
        pass

    def get_buff_type(self):
        pass


_buff_effects: Dict[BuffType, Type[AbstractBuffEffect]] = {}


def register_buff_effect(buff_type: BuffType, effect: Type[AbstractBuffEffect]):
    _buff_effects[buff_type] = effect


def get_buff_effect(buff_type: BuffType) -> AbstractBuffEffect:
    return _buff_effects[buff_type]()
