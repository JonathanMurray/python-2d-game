import pygame

from pythongame.core.common import *
from pythongame.core.game_data import KEYS_BY_ABILITY_TYPE


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


PYGAME_MOVEMENT_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
DIRECTION_BY_PYGAME_MOVEMENT_KEY = {
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN
}
movement_keys_down = []


def get_user_actions():
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
            elif event.key == pygame.K_ESCAPE:
                actions.append(ActionExitGame())
            elif event.key == pygame.K_RETURN:
                actions.append(ActionPauseGame())
            elif event.key == pygame.K_SPACE:
                actions.append(ActionPressSpaceKey())
            else:
                for ability_type in KEYS_BY_ABILITY_TYPE:
                    if event.key == KEYS_BY_ABILITY_TYPE[ability_type].pygame_key:
                        actions.append(ActionTryUseAbility(ability_type))

        if event.type == pygame.KEYUP:
            if event.key in PYGAME_MOVEMENT_KEYS:
                if event.key in movement_keys_down:
                    movement_keys_down.remove(event.key)

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

    return actions
