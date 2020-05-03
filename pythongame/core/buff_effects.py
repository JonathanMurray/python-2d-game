from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import GameState, NonPlayerCharacter, Event, BuffEventOutcome
from pythongame.core.world_entity import WorldEntity


class AbstractBuffEffect:
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        pass

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis) -> Optional[bool]:
        pass

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        pass

    def get_buff_type(self):
        raise Exception("This method needs to be overridden")

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        return None


# TODO Use this instead of re-inventing similar buff effects
class StunningBuffEffect(AbstractBuffEffect):

    def __init__(self, buff_type: BuffType):
        self._buff_type = buff_type

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.add_one()
        buffed_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.remove_one()

    def get_buff_type(self) -> BuffType:
        return self._buff_type


class StatModifyingBuffEffect(AbstractBuffEffect):

    def __init__(self, buff_type: BuffType, stat_modifiers: Dict[HeroStat, Union[int, float]]):
        self.buff_type = buff_type
        self.stat_modifiers = stat_modifiers

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        for stat, delta in self.stat_modifiers.items():
            game_state.modify_hero_stat(stat, delta)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        for stat, delta in self.stat_modifiers.items():
            game_state.modify_hero_stat(stat, -delta)

    def get_buff_type(self):
        return self.buff_type


_buff_effects: Dict[BuffType, Type[AbstractBuffEffect]] = {}


def register_buff_effect(buff_type: BuffType, effect: Type[AbstractBuffEffect]):
    _buff_effects[buff_type] = effect


def get_buff_effect(buff_type: BuffType, args: Optional[Any] = None) -> AbstractBuffEffect:
    if not buff_type in _buff_effects:
        raise Exception(
            "No buff effect found for buff " + str(buff_type) + "! Known buffs: " + str(_buff_effects.keys()))
    if args is not None:
        # args passed in, assume the buff takes args in constructor
        return _buff_effects[buff_type](args)
    else:
        # no args passed in, assume the buff doesn't take any args in constructor
        return _buff_effects[buff_type]()
