#!/usr/bin/env python3

import pygame
import sys

from game_engine import GameEngine
from game_world_init import init_game_state_from_file
from user_input import get_user_actions, ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame
from view import View
from view_state import ViewState

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 400)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
view = View(screen, CAMERA_SIZE, SCREEN_SIZE)
view_state = ViewState(GAME_WORLD_SIZE)
clock = pygame.time.Clock()

game_engine = GameEngine(game_state, view_state)

is_paused = False

while True:

    # ------------------------------------
    #         HANDLE USER INPUT
    # ------------------------------------

    user_actions = get_user_actions()
    for action in user_actions:
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        if not is_paused:
            if isinstance(action, ActionTryUseAbility):
                game_engine.try_use_ability(action)
            elif isinstance(action, ActionTryUsePotion):
                game_engine.try_use_potion(action)
            elif isinstance(action, ActionMoveInDirection):
                game_engine.move_in_direction(action)
            elif isinstance(action, ActionStopMoving):
                game_engine.stop_moving()
        if isinstance(action, ActionPauseGame):
            is_paused = not is_paused

    # ------------------------------------
    #     UPDATE STATE BASED ON CLOCK
    # ------------------------------------

    clock.tick()
    time_passed = clock.get_time()

    if not is_paused:
        game_engine.run_one_frame(time_passed)

    # ------------------------------------
    #          RENDER EVERYTHING
    # ------------------------------------

    view.render_everything(all_entities=game_state.get_all_entities(),
                           player_entity=game_state.player_entity,
                           is_player_invisible=game_state.player_state.is_invisible,
                           camera_world_area=game_state.camera_world_area,
                           enemies=game_state.enemies,
                           player_health=game_state.player_state.health,
                           player_max_health=game_state.player_state.max_health,
                           player_mana=game_state.player_state.mana,
                           player_max_mana=game_state.player_state.max_mana,
                           potion_slots=game_state.player_state.potion_slots,
                           player_active_buffs=game_state.player_state.active_buffs,
                           visual_lines=game_state.visual_lines,
                           fps_string=str(int(clock.get_fps())),
                           player_minimap_relative_position=view_state.player_minimap_relative_position,
                           abilities=game_state.player_state.abilities,
                           message=view_state.message,
                           highlighted_potion_action=view_state.highlighted_potion_action,
                           highlighted_ability_action=view_state.highlighted_ability_action,
                           is_paused=is_paused)
