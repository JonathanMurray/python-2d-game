from typing import Any, Dict

from pythongame.common import *
from pythongame.game_state import GameState

# TODO Create an interface for the ability effect functions

_ability_effects: Dict[AbilityType, Any] = {}


def register_ability_effect(ability_type: AbilityType, effect_function):
    _ability_effects[ability_type] = effect_function


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    _ability_effects[ability_type](game_state)
