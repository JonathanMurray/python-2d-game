import sys
from typing import Optional, Tuple

import pygame

from pythongame.core.common import SceneId, Millis, AbstractScene, SceneTransition
from pythongame.core.game_state import GameState
from pythongame.core.user_input import ActionExitGame, ActionPauseGame, ActionSaveGameState, \
    get_paused_user_inputs
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.player_file import save_to_file
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView


class PausedScene(AbstractScene):
    def __init__(
            self,
            world_view: GameWorldView,
            ui_view: GameUiView):
        self.world_view = world_view
        self.ui_view = ui_view

        # Set on initialization
        self.game_state = None
        self.ui_state = None

    def initialize(self, data: Tuple[GameState, GameUiState]):
        self.game_state, self.ui_state = data

    def run_one_frame(self, _time_passed: Millis, _fps_string: str) -> Optional[SceneTransition]:
        scene_transition = None

        user_actions = get_paused_user_inputs()
        for action in user_actions:
            if isinstance(action, ActionExitGame):
                pygame.quit()
                sys.exit()
            if isinstance(action, ActionPauseGame):
                scene_transition = SceneTransition(SceneId.PLAYING, None)
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

        self.ui_view.render_ui(
            player_state=self.game_state.player_state,
            ui_state=self.ui_state,
            text_in_topleft_corner="...",
            is_paused=True,
            dialog=None,  # We don't bother to show dialog etc when game is paused
        )

        self.world_view.update_display()

        return scene_transition
