from typing import Any, Dict

from pythongame.common import *
from pythongame.game_state import GameState
from pythongame.visual_effects import VisualCircle


# TODO Create an interface for the potion effect functions

class PotionWasConsumed:
    pass


class PotionFailedToBeConsumed:
    def __init__(self, reason):
        self.reason = reason


def create_potion_visual_effect_at_player(game_state):
    game_state.visual_effects.append(VisualCircle(
        (230, 230, 230), game_state.player_entity.get_center_position(), 55, Millis(90), 3,
        game_state.player_entity))


_potion_effects: Dict[PotionType, Any] = {}


def register_potion_effect(potion_type: PotionType, effect_function):
    _potion_effects[potion_type] = effect_function


def try_consume_potion(potion_type: PotionType, game_state: GameState):
    return _potion_effects[potion_type](game_state)
