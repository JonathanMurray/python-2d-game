import pygame

from pythongame.abilities import register_ability_effect
from pythongame.common import translate_in_direction, Millis, AbilityType
from pythongame.game_data import register_ability_data, AbilityData, UiIconSprite, register_ui_icon_sprite_path
from pythongame.game_state import GameState
from pythongame.visual_effects import VisualCircle, VisualRect, VisualLine


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


def register_teleport_ability():
    register_ability_effect(AbilityType.TELEPORT, _apply_teleport)
    register_ability_data(AbilityType.TELEPORT, AbilityData(UiIconSprite.TELEPORT, 2, "T", pygame.K_t, Millis(500)))
    register_ui_icon_sprite_path(UiIconSprite.TELEPORT, "resources/teleport_icon.png")
