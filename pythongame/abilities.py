from pythongame.common import *
from pythongame.game_state import GameState
from pythongame.visual_effects import VisualCircle, VisualLine, VisualRect


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    ability_effects[ability_type](game_state)


def _apply_teleport(game_state: GameState):
    player_entity = game_state.player_entity
    previous_position = player_entity.get_center_position()
    new_position = translate_in_direction((player_entity.x, player_entity.y), player_entity.direction, 140)
    player_entity.set_position(new_position)
    new_center_position = player_entity.get_center_position()

    color = (140, 140, 230)
    game_state.visual_effects.append(VisualCircle(color, previous_position, 35, Millis(150), 1))
    game_state.visual_effects.append(VisualRect(color, previous_position, 50, Millis(150)))
    game_state.visual_effects.append(VisualLine(color, previous_position, new_center_position, Millis(200), 1))
    game_state.visual_effects.append(VisualCircle(color, new_center_position, 50, Millis(300), 2, player_entity))


ability_effects = {
    AbilityType.TELEPORT: _apply_teleport
}


def register_ability_effect(ability_type, effect_function):
    ability_effects[ability_type] = effect_function
