#!/usr/bin/env python3

import pygame
import sys

from common import AbilityType
from game_engine import GameEngine
from game_world_init import init_game_state_from_file
from user_input import get_user_actions, ActionExitGame
from view import View, ScreenArea
from view_state import ViewState

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 400)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE)
view_state = ViewState(GAME_WORLD_SIZE)
clock = pygame.time.Clock()

game_engine = GameEngine(game_state, view_state)

while True:

    # ------------------------------------
    #         HANDLE USER INPUT
    # ------------------------------------

    user_actions = get_user_actions()
    for action in user_actions:
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        else:
            game_engine.apply_user_action(action)

    # ------------------------------------
    #     UPDATE STATE BASED ON CLOCK
    # ------------------------------------

    clock.tick()
    time_passed = clock.get_time()

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
                           abilities=[AbilityType.ATTACK, AbilityType.HEAL, AbilityType.AOE_ATTACK],
                           message=view_state.message,
                           highlighted_potion_action=view_state.highlighted_potion_action,
                           highlighted_ability_action=view_state.highlighted_ability_action)
