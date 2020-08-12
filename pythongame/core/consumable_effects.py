from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState
from pythongame.core.visual_effects import VisualCircle


class AbstractConsumableResult:
    pass


class ConsumableWasConsumed(AbstractConsumableResult):
    def __init__(self, message=None):
        self.message = message


class ConsumableFailedToBeConsumed(AbstractConsumableResult):
    def __init__(self, reason: str):
        self.reason = reason


def create_potion_visual_effect_at_player(game_state):
    game_state.game_world.visual_effects.append(VisualCircle(
        (230, 230, 230), game_state.game_world.player_entity.get_center_position(), 27, 55, Millis(90), 3,
        game_state.game_world.player_entity))


_consumable_effects: Dict[ConsumableType, Callable[[GameState], AbstractConsumableResult]] = {}


def register_consumable_effect(consumable_type: ConsumableType,
                               effect_function: Callable[[GameState], AbstractConsumableResult]):
    _consumable_effects[consumable_type] = effect_function


def try_consume_consumable(consumable_type: ConsumableType, game_state: GameState):
    return _consumable_effects[consumable_type](game_state)
