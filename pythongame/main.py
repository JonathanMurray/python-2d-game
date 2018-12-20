import sys
from typing import List

import pygame

import pythongame.core.pathfinding.enemy_pathfinding
from pythongame.core.common import Millis
from pythongame.core.game_engine import GameEngine
from pythongame.core.user_input import get_user_actions, ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement
from pythongame.core.view import View
from pythongame.core.view_state import ViewState
from pythongame.game_world_init import create_game_state_from_file
from pythongame.register_game_data import register_all_game_data

SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 500)

register_all_game_data()


def main(args: List[str]):
    if len(args) == 1:
        map_file = args[0]
    else:
        map_file = "resources/maps/demo3.txt"
    game_state = create_game_state_from_file(CAMERA_SIZE, map_file)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)
    view_state = ViewState(game_state.game_world_size)
    clock = pygame.time.Clock()

    game_engine = GameEngine(game_state, view_state)

    is_paused = False
    is_game_over = False
    render_hit_and_collision_boxes = False
    mouse_screen_position = (0, 0)

    game_engine.initialize()

    while True:

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        user_actions = get_user_actions()
        for action in user_actions:
            if isinstance(action, ActionExitGame):
                pygame.quit()
                sys.exit()
            if isinstance(action, ActionToggleRenderDebugging):
                render_hit_and_collision_boxes = not render_hit_and_collision_boxes
                # TODO: Handle this better than accessing a global variable from here
                pythongame.core.pathfinding.enemy_pathfinding.DEBUG_RENDER_PATHFINDING = \
                    not pythongame.core.pathfinding.enemy_pathfinding.DEBUG_RENDER_PATHFINDING
            if not is_paused and not is_game_over:
                if isinstance(action, ActionTryUseAbility):
                    game_engine.try_use_ability(action.ability_type)
                elif isinstance(action, ActionTryUsePotion):
                    game_engine.try_use_potion(action.slot_number)
                elif isinstance(action, ActionMoveInDirection):
                    game_engine.move_in_direction(action.direction)
                elif isinstance(action, ActionStopMoving):
                    game_engine.stop_moving()
            if isinstance(action, ActionPauseGame):
                is_paused = not is_paused
            if isinstance(action, ActionMouseMovement):
                mouse_screen_position = action.mouse_screen_position

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        clock.tick()
        time_passed = Millis(clock.get_time())

        if not is_paused and not is_game_over:
            player_died = game_engine.run_one_frame(time_passed)
            if player_died:
                is_game_over = True

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            enemies=game_state.enemies,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=render_hit_and_collision_boxes,
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            game_world_size=game_state.game_world_size)

        view.render_ui(
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            player_mana=game_state.player_state.mana,
            player_max_mana=game_state.player_state.max_mana,
            potion_slots=game_state.player_state.potion_slots,
            player_active_buffs=game_state.player_state.active_buffs,
            fps_string=str(int(clock.get_fps())),
            player_minimap_relative_position=view_state.player_minimap_relative_position,
            abilities=game_state.player_state.abilities,
            message=view_state.message,
            highlighted_potion_action=view_state.highlighted_potion_action,
            highlighted_ability_action=view_state.highlighted_ability_action,
            is_paused=is_paused,
            is_game_over=is_game_over,
            ability_cooldowns_remaining=game_state.player_state.ability_cooldowns_remaining,
            item_slots=game_state.player_state.item_slots,
            mouse_screen_position=mouse_screen_position)

        view.update_display()
