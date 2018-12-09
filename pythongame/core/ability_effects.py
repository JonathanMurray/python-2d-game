from typing import Any, Dict, Callable

from pythongame.core.common import *
from pythongame.core.game_state import GameState

_ability_effects: Dict[AbilityType, Callable[[GameState], Any]] = {}


def register_ability_effect(ability_type: AbilityType, effect_function: Callable[[GameState], None]):
    _ability_effects[ability_type] = effect_function


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    _ability_effects[ability_type](game_state)
