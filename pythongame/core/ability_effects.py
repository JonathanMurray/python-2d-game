from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState


class AbilityResult:
    pass


class AbilityFailedToExecute(AbilityResult):
    def __init__(self, reason: Optional[str] = None):
        self.reason = reason


class AbilityWasUsedSuccessfully(AbilityResult):
    def __init__(self, should_regain_mana_and_cd: bool = False):
        self.should_regain_mana_and_cd = should_regain_mana_and_cd


_ability_effects: Dict[AbilityType, Callable[[GameState], AbilityResult]] = {}


# Effect function should return True if ability was used successfully
def register_ability_effect(ability_type: AbilityType,
                            effect_function: Callable[[GameState], AbilityResult]):
    _ability_effects[ability_type] = effect_function


def apply_ability_effect(game_state: GameState, ability_type: AbilityType) -> AbilityResult:
    return _ability_effects[ability_type](game_state)
