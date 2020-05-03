from typing import Optional, Any, List

import pygame

from pythongame.core.common import AbstractScene, SceneTransition
from pythongame.core.game_state import GameState
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.scenes.scenes_game.game_ui_view import GameUiView


class PausedScene(AbstractScene):
    def __init__(
            self,
            playing_scene: AbstractScene,
            world_view: GameWorldView,
            ui_view: GameUiView,
            game_state: GameState):
        self.playing_scene = playing_scene
        self.world_view = world_view
        self.ui_view = ui_view
        self.game_state = game_state

    def on_enter(self):
        self.ui_view.set_paused(True)

    def handle_user_input(self, events: List[Any]) -> Optional[SceneTransition]:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return SceneTransition(self.playing_scene)

    def render(self):
        self.world_view.render_world(
            all_entities_to_render=self.game_state.get_all_entities_to_render(),
            decorations_to_render=self.game_state.get_decorations_to_render(),
            player_entity=self.game_state.game_world.player_entity,
            is_player_invisible=self.game_state.player_state.is_invisible,
            player_active_buffs=self.game_state.player_state.active_buffs,
            camera_world_area=self.game_state.camera_world_area,
            non_player_characters=self.game_state.game_world.non_player_characters,
            visual_effects=self.game_state.game_world.visual_effects,
            render_hit_and_collision_boxes=False,
            player_health=self.game_state.player_state.health_resource.value,
            player_max_health=self.game_state.player_state.health_resource.max_value,
            entire_world_area=self.game_state.game_world.entire_world_area,
            entity_action_text=None)

        self.ui_view.render()
