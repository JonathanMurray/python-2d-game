from typing import Dict, Type, Optional, Any

from pythongame.core.common import *
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter


class AbstractBuffEffect:
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        pass

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        pass

    def get_buff_type(self):
        pass

    # TODO Handle more events, and more possible outcomes
    # Return Millis if buff should have prolonged duration as an outcome of the event
    def notify_that_enemy_died(self) -> Optional[Millis]:
        return None


_buff_effects: Dict[BuffType, Type[AbstractBuffEffect]] = {}


def register_buff_effect(buff_type: BuffType, effect: Type[AbstractBuffEffect]):
    _buff_effects[buff_type] = effect


def get_buff_effect(buff_type: BuffType, args: Optional[Any] = None) -> AbstractBuffEffect:
    if args:
        # args passed in, assume the buff takes args in constructor
        return _buff_effects[buff_type](args)
    else:
        # no args passed in, assume the buff doesn't take any args in constructor
        return _buff_effects[buff_type]()
