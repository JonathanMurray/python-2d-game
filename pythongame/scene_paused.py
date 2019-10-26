import sys

import pygame

from pythongame.core.common import SceneId
from pythongame.core.game_state import GameState
from pythongame.core.talents import talents_graphics_from_state
from pythongame.core.user_input import ActionExitGame, ActionPauseGame, get_main_user_inputs, ActionSaveGameState
from pythongame.core.view.game_ui_view import GameUiView
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.view_state import ViewState
from pythongame.player_file import save_to_file


class PausedScene:
    def __init__(
            self,
            game_state: GameState,
            world_view: GameWorldView,
            ui_view: GameUiView,
            view_state: ViewState):
        self.game_state = game_state
        self.world_view = world_view
        self.ui_view = ui_view
        self.view_state = view_state

    def run_one_frame(self):
        scene_transition = None

        user_actions = get_main_user_inputs()
        for action in user_actions:
            if isinstance(action, ActionExitGame):
                pygame.quit()
                sys.exit()
            if isinstance(action, ActionPauseGame):
                scene_transition = SceneId.PLAYING
            if isinstance(action, ActionSaveGameState):
                save_to_file(self.game_state)

        self.world_view.render_world(
            all_entities_to_render=self.game_state.get_all_entities_to_render(),
            decorations_to_render=self.game_state.get_decorations_to_render(),
            player_entity=self.game_state.player_entity,
            is_player_invisible=self.game_state.player_state.is_invisible,
            player_active_buffs=self.game_state.player_state.active_buffs,
            camera_world_area=self.game_state.camera_world_area,
            non_player_characters=self.game_state.non_player_characters,
            visual_effects=self.game_state.visual_effects,
            render_hit_and_collision_boxes=False,
            player_health=self.game_state.player_state.health_resource.value,
            player_max_health=self.game_state.player_state.health_resource.max_value,
            entire_world_area=self.game_state.entire_world_area,
            entity_action_text=None)

        talents_graphics = talents_graphics_from_state(
            self.game_state.player_state.talents_state, self.game_state.player_state.level,
            self.game_state.player_state.chosen_talent_option_indices)

        self.ui_view.render_ui(
            player_state=self.game_state.player_state,
            view_state=self.view_state,
            player_speed_multiplier=self.game_state.player_entity.speed_multiplier,
            fps_string="...",
            is_paused=True,
            mouse_screen_position=(0, 0),  # We don't bother to show tooltips etc when game is paused
            dialog=None,  # We don't bother to show dialog etc when game is paused
            talents=talents_graphics)

        self.world_view.update_display()

        return scene_transition
