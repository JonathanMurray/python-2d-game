from typing import List, Tuple

import pygame

from pythongame.core.common import *
from pythongame.core.game_data import KEYS_BY_ABILITY_TYPE

EXIT_ON_ESCAPE = False


class ActionExitGame:
    pass


class ActionTryUseAbility:
    def __init__(self, ability_type):
        self.ability_type = ability_type


class ActionTryUsePotion:
    def __init__(self, slot_number):
        self.slot_number = slot_number


class ActionMoveInDirection:
    def __init__(self, direction):
        self.direction = direction


class ActionStopMoving:
    pass


class ActionPauseGame:
    pass


class ActionPressSpaceKey:
    pass


class ActionPressShiftKey:
    pass


class ActionReleaseShiftKey:
    pass


class ActionSaveGameState:
    pass


class ActionToggleRenderDebugging:
    pass


# Used for determining when user hovers over something in UI.
# TODO: Handle the dependency between user input and the visual interface in a better way
class ActionMouseMovement:
    def __init__(self, mouse_screen_position: Tuple[int, int]):
        self.mouse_screen_position = mouse_screen_position


# Used for dragging items in UI
class ActionMouseClicked:
    pass


# Used for dragging items in UI
class ActionMouseReleased:
    pass


class ActionChangeDialogOption:
    def __init__(self, index_delta: int):
        self.index_delta = index_delta


class ActionPickHeroChange:
    def __init__(self, delta: int):
        self.delta = delta

class ActionPickHeroAccept:
    pass


PYGAME_MOVEMENT_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
DIRECTION_BY_PYGAME_MOVEMENT_KEY = {
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN
}

# TODO: Change this file into a class with clearer state handling
movement_keys_down = []
ability_keys_down: List[AbilityType] = []


def get_dialog_user_inputs():
    actions = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append(ActionExitGame())
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and EXIT_ON_ESCAPE:
                actions.append(ActionExitGame())
            elif event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                actions.append(ActionChangeDialogOption(-1))
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                actions.append(ActionChangeDialogOption(1))
            elif event.key == pygame.K_SPACE:
                actions.append(ActionPressSpaceKey())
        if event.type == pygame.KEYUP:
            if event.key in PYGAME_MOVEMENT_KEYS:
                if event.key in movement_keys_down:
                    movement_keys_down.remove(event.key)
            else:
                for ability_type in KEYS_BY_ABILITY_TYPE:
                    if event.key == KEYS_BY_ABILITY_TYPE[ability_type].pygame_key:
                        if ability_type in ability_keys_down:
                            ability_keys_down.remove(ability_type)
    return actions


def get_main_user_inputs():
    actions = []
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append(ActionExitGame())
        if event.type == pygame.KEYDOWN:
            if event.key in PYGAME_MOVEMENT_KEYS:
                if event.key in movement_keys_down:
                    movement_keys_down.remove(event.key)
                movement_keys_down.append(event.key)
            elif event.key == pygame.K_1:
                actions.append(ActionTryUsePotion(1))
            elif event.key == pygame.K_2:
                actions.append(ActionTryUsePotion(2))
            elif event.key == pygame.K_3:
                actions.append(ActionTryUsePotion(3))
            elif event.key == pygame.K_4:
                actions.append(ActionTryUsePotion(4))
            elif event.key == pygame.K_5:
                actions.append(ActionTryUsePotion(5))
            elif event.key == pygame.K_0:
                actions.append(ActionToggleRenderDebugging())
            elif event.key == pygame.K_ESCAPE and EXIT_ON_ESCAPE:
                actions.append(ActionExitGame())
            elif event.key == pygame.K_RETURN:
                actions.append(ActionPauseGame())
            elif event.key == pygame.K_SPACE:
                actions.append(ActionPressSpaceKey())
            elif event.key == pygame.K_LSHIFT:
                actions.append(ActionPressShiftKey())
            elif event.key == pygame.K_s:
                actions.append(ActionSaveGameState())
            else:
                for ability_type in KEYS_BY_ABILITY_TYPE:
                    if event.key == KEYS_BY_ABILITY_TYPE[ability_type].pygame_key:
                        if ability_type in ability_keys_down:
                            ability_keys_down.remove(ability_type)
                        ability_keys_down.append(ability_type)

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                actions.append(ActionReleaseShiftKey())
            elif event.key in PYGAME_MOVEMENT_KEYS:
                if event.key in movement_keys_down:
                    movement_keys_down.remove(event.key)
            else:
                for ability_type in KEYS_BY_ABILITY_TYPE:
                    if event.key == KEYS_BY_ABILITY_TYPE[ability_type].pygame_key:
                        if ability_type in ability_keys_down:
                            ability_keys_down.remove(ability_type)

        if event.type == pygame.MOUSEMOTION:
            actions.append(ActionMouseMovement(event.pos))

        if event.type == pygame.MOUSEBUTTONDOWN:
            actions.append(ActionMouseClicked())

        if event.type == pygame.MOUSEBUTTONUP:
            actions.append(ActionMouseReleased())

    if movement_keys_down:
        last_pressed_movement_key = movement_keys_down[-1]
        direction = DIRECTION_BY_PYGAME_MOVEMENT_KEY[last_pressed_movement_key]
        actions.append(ActionMoveInDirection(direction))
    else:
        actions.append(ActionStopMoving())

    for ability_type in ability_keys_down:
        actions.append(ActionTryUseAbility(ability_type))

    return actions


def get_picking_hero_user_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return ActionExitGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                return ActionPickHeroChange(-1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                return ActionPickHeroChange(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return ActionPickHeroAccept()