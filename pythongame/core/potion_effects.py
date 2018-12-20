from typing import Dict, Callable

from pythongame.core.common import *
from pythongame.core.game_state import GameState
from pythongame.core.visual_effects import VisualCircle


class AbstractPotionResult:
    pass


class PotionWasConsumed(AbstractPotionResult):
    pass


class PotionFailedToBeConsumed(AbstractPotionResult):
    def __init__(self, reason):
        self.reason = reason


def create_potion_visual_effect_at_player(game_state):
    game_state.visual_effects.append(VisualCircle(
        (230, 230, 230), game_state.player_entity.get_center_position(), 27, 55, Millis(90), 3,
        game_state.player_entity))


_potion_effects: Dict[PotionType, Callable[[GameState], AbstractPotionResult]] = {}


def register_potion_effect(potion_type: PotionType, effect_function: Callable[[GameState], AbstractPotionResult]):
    _potion_effects[potion_type] = effect_function


def try_consume_potion(potion_type: PotionType, game_state: GameState):
    return _potion_effects[potion_type](game_state)
