from typing import Any, Dict

from pythongame.common import *
from pythongame.game_state import GameState


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    ability_effects[ability_type](game_state)


ability_effects: Dict[AbilityType, Any] = {}


# TODO Create an interface for the ability effect functions


def register_ability_effect(ability_type: AbilityType, effect_function):
    ability_effects[ability_type] = effect_function
