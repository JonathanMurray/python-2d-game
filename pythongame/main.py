import sys
from typing import Optional, List, Any

import pygame

from pythongame.core.common import Millis, SceneTransition, AbstractScene
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, \
    UI_ICON_SPRITE_PATHS, PORTRAIT_ICON_SPRITE_PATHS
from pythongame.core.game_state import GameState
from pythongame.core.sound_player import init_sound_player
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.image_loading import load_images_by_sprite, \
    load_images_by_ui_sprite, load_images_by_portrait_sprite
from pythongame.core.world_behavior import AbstractWorldBehavior
from pythongame.player_file import SaveFileHandler
from pythongame.register_game_data import register_all_game_data
from pythongame.scene_challenge_complete_screen.scene_challenge_complete_screen import ChallengeCompleteScreenScene
from pythongame.scene_creating_world.scene_creating_world import CreatingWorldScene, InitFlags
from pythongame.scene_main_menu.scene_main_menu import MainMenuScene
from pythongame.scene_picking_hero.scene_picking_hero import PickingHeroScene
from pythongame.scene_picking_hero.view_picking_hero import PickingHeroView
from pythongame.scene_starting_program.scene_starting_program import CommandlineFlags, StartingProgramScene
from pythongame.scene_victory_screen.scene_victory_screen import VictoryScreenScene
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, UI_ICON_SIZE, PORTRAIT_ICON_SIZE, UI_ICON_BIG_SIZE
from pythongame.scenes_game.scene_playing import PlayingScene

ABILITY_KEY_LABELS = ["Q", "W", "E", "R", "T"]
SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 530)

register_all_game_data()


class Main:
    def __init__(self, map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
                 start_money: Optional[int], load_from_file: Optional[str]):

        cmd_flags = CommandlineFlags(map_file_name, chosen_hero_id, load_from_file, hero_start_level, start_money)

        pygame.init()

        self.pygame_screen = pygame.display.set_mode(SCREEN_SIZE)
        images_by_sprite = load_images_by_sprite(ENTITY_SPRITE_INITIALIZERS)
        images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_SIZE)
        big_images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_BIG_SIZE)
        self.images_by_portrait_sprite = load_images_by_portrait_sprite(PORTRAIT_ICON_SPRITE_PATHS, PORTRAIT_ICON_SIZE)
        self.world_view = GameWorldView(self.pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite)
        self.ui_view = GameUiView(
            self.pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_ui_sprite, big_images_by_ui_sprite,
            self.images_by_portrait_sprite, ABILITY_KEY_LABELS)
        self.save_file_handler = SaveFileHandler()
        init_sound_player()
        self.clock = pygame.time.Clock()

        self.scene: AbstractScene = StartingProgramScene(
            self.main_menu_scene, self.creating_world_scene, self.picking_hero_scene, cmd_flags, self.save_file_handler)

    def main_loop(self):
        while True:
            self.clock.tick()
            time_passed = Millis(self.clock.get_time())
            fps_string = str(int(self.clock.get_fps()))
            self.ui_view.update_fps_string(fps_string)

            input_events: List[Any] = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            transition: Optional[SceneTransition] = self.scene.handle_user_input(input_events)
            if transition:
                self.change_scene(transition)
                continue

            transition: Optional[SceneTransition] = self.scene.run_one_frame(time_passed)
            if transition:
                self.change_scene(transition)
                continue

            self.scene.render()
            pygame.display.update()

    def change_scene(self, scene_transition: SceneTransition):
        self.scene = scene_transition.scene
        self.scene.on_enter()

    def main_menu_scene(self, flags: InitFlags):
        return MainMenuScene(
            self.pygame_screen, self.save_file_handler, self.picking_hero_scene, self.creating_world_scene, flags)

    def creating_world_scene(self, flags: InitFlags):
        return CreatingWorldScene(self.playing_scene, self.picking_hero_scene, self.challenge_complete_scene,
                                  self.victory_screen_scene, CAMERA_SIZE, self.ui_view, flags)

    def picking_hero_scene(self, init_flags: InitFlags):
        view = PickingHeroView(self.pygame_screen, self.images_by_portrait_sprite)
        return PickingHeroScene(self.creating_world_scene, view, init_flags)

    def playing_scene(
            self, game_state: GameState, game_engine: GameEngine, world_behavior: AbstractWorldBehavior,
            ui_state: GameUiState, ui_view: GameUiView, new_hero_was_created: bool, character_file: Optional[str],
            total_time_played_on_character: Millis):
        return PlayingScene(
            self.world_view, game_state, game_engine, world_behavior, ui_state, ui_view, new_hero_was_created,
            character_file, self.save_file_handler, total_time_played_on_character)

    def challenge_complete_scene(self, total_time_played: Millis):
        return ChallengeCompleteScreenScene(self.pygame_screen, total_time_played)

    def victory_screen_scene(self):
        return VictoryScreenScene(self.pygame_screen)


def start(map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
          start_money: Optional[int], load_from_file: Optional[str]):
    main = Main(map_file_name, chosen_hero_id, hero_start_level, start_money, load_from_file)
    main.main_loop()
