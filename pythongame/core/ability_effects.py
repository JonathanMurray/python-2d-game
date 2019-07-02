from typing import Dict, Callable

from pythongame.core.common import *
from pythongame.core.game_state import GameState

_ability_effects: Dict[AbilityType, Callable[[GameState], bool]] = {}


# Effect function should return True if ability was used successfully
def register_ability_effect(ability_type: AbilityType, effect_function: Callable[[GameState], bool]):
    _ability_effects[ability_type] = effect_function


def apply_ability_effect(game_state: GameState, ability_type: AbilityType) -> bool:
    did_execute = _ability_effects[ability_type](game_state)
    return did_execute
