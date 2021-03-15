import sys
from typing import Optional, List, Any, Tuple, Callable

import pygame

from pythongame.core.common import Millis, SceneTransition, AbstractScene, AbstractWorldBehavior
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, \
    UI_ICON_SPRITE_PATHS, PORTRAIT_ICON_SPRITE_PATHS
from pythongame.core.game_state import GameState
from pythongame.core.sound_player import init_sound_player
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.image_loading import load_images_by_sprite, \
    load_images_by_ui_sprite, load_images_by_portrait_sprite
from pythongame.player_file import SaveFileHandler
from pythongame.register_game_data import register_all_game_data
from pythongame.scenes.scene_challenge_complete_screen.scene_challenge_complete_screen import \
    ChallengeCompleteScreenScene
from pythongame.scenes.scene_creating_world.scene_creating_world import CreatingWorldScene, InitFlags
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scene_main_menu.scene_main_menu import MainMenuScene
from pythongame.scenes.scene_main_menu.view_main_menu import MainMenuView
from pythongame.scenes.scene_picking_hero.scene_picking_hero import PickingHeroScene
from pythongame.scenes.scene_picking_hero.view_picking_hero import PickingHeroView
from pythongame.scenes.scene_starting_program.scene_starting_program import CommandlineFlags, StartingProgramScene
from pythongame.scenes.scene_switching_game_world.scene_switching_game_world import SwitchingGameWorldScene
from pythongame.scenes.scene_victory_screen.scene_victory_screen import VictoryScreenScene
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import GameUiView, UI_ICON_SIZE, PORTRAIT_ICON_SIZE, UI_ICON_BIG_SIZE
from pythongame.scenes.scenes_game.scene_playing import PlayingScene

ABILITY_KEY_LABELS = ["Q", "W", "E", "R", "T"]
SCREEN_SIZE = (800, 600)  # If this is not a supported resolution, performance takes a big hit
CAMERA_SIZE = (800, 430)

register_all_game_data()


class SceneFactory(AbstractSceneFactory):

    def __init__(self, pygame_screen, images_by_portrait_sprite, save_file_handler, ui_view: GameUiView,
                 world_view: GameWorldView, toggle_fullscreen, camera_size: Tuple[int, int]):
        self.pygame_screen = pygame_screen
        self.images_by_portrait_sprite = images_by_portrait_sprite
        self.save_file_handler = save_file_handler
        self.ui_view = ui_view
        self.world_view = world_view
        self.toggle_fullscreen = toggle_fullscreen
        self.camera_size = camera_size

    def main_menu_scene(self, flags: InitFlags) -> AbstractScene:
        view = MainMenuView(self.pygame_screen, self.images_by_portrait_sprite)
        return MainMenuScene(
            self.save_file_handler, self, flags, view)

    def creating_world_scene(self, flags: InitFlags) -> AbstractScene:
        return CreatingWorldScene(self, self.camera_size, self.ui_view, flags)

    def picking_hero_scene(self, init_flags: InitFlags) -> AbstractScene:
        view = PickingHeroView(self.pygame_screen, self.images_by_portrait_sprite)
        return PickingHeroScene(self, view, init_flags)

    def playing_scene(
            self, game_state: GameState, game_engine: GameEngine, world_behavior: AbstractWorldBehavior,
            ui_view: GameUiView, new_hero_was_created: bool, character_file: Optional[str],
            total_time_played_on_character: Millis) -> AbstractScene:
        return PlayingScene(
            self, self.world_view, game_state, game_engine, world_behavior, ui_view, new_hero_was_created,
            character_file, self.save_file_handler, total_time_played_on_character, self.toggle_fullscreen)

    def challenge_complete_scene(self, total_time_played: Millis) -> AbstractScene:
        return ChallengeCompleteScreenScene(self.pygame_screen, total_time_played)

    def victory_screen_scene(self) -> AbstractScene:
        return VictoryScreenScene(self.pygame_screen)

    def switching_game_world(
            self,
            game_engine: GameEngine,
            character_file: str,
            total_time_played_on_character: Millis,
            create_new_game_engine_and_behavior: Callable[[GameEngine], Tuple[GameEngine, AbstractWorldBehavior]]) \
            -> AbstractScene:
        return SwitchingGameWorldScene(self, game_engine, self.ui_view, character_file, total_time_played_on_character,
                                       create_new_game_engine_and_behavior)


class Main:
    def __init__(self, map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
                 start_money: Optional[int], save_file_name: Optional[str], fullscreen: bool):

        cmd_flags = CommandlineFlags(map_file_name, chosen_hero_id, hero_start_level, start_money, save_file_name)

        pygame.init()

        print("Available display modes: " + str(pygame.display.list_modes()))

        self.fullscreen = fullscreen
        self.pygame_screen = self.setup_screen()
        images_by_sprite = load_images_by_sprite(ENTITY_SPRITE_INITIALIZERS)
        images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_SIZE)
        big_images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_BIG_SIZE)
        self.images_by_portrait_sprite = load_images_by_portrait_sprite(PORTRAIT_ICON_SPRITE_PATHS, PORTRAIT_ICON_SIZE)
        self.world_view = GameWorldView(self.pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite)
        self.ui_view = GameUiView(
            self.pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_ui_sprite,
            big_images_by_ui_sprite, self.images_by_portrait_sprite, ABILITY_KEY_LABELS)
        self.ui_view.on_fullscreen_changed(self.fullscreen)
        self.save_file_handler = SaveFileHandler()
        init_sound_player()
        self.clock = pygame.time.Clock()

        self.scene_factory = SceneFactory(self.pygame_screen, self.images_by_portrait_sprite, self.save_file_handler,
                                          self.ui_view, self.world_view, self.toggle_fullscreen, CAMERA_SIZE)

        self.scene: AbstractScene = StartingProgramScene(self.scene_factory, cmd_flags, self.save_file_handler)

    def main_loop(self):
        try:
            self._main_loop()
        except Exception as e:
            print("Game crashed with an unexpected error! %s" % e)
            if hasattr(self.scene, 'game_state'):
                game_state: GameState = getattr(self.scene, 'game_state', None)
                print("Saving character to file as backup...")
                self.save_file_handler.save_to_file(game_state.player_state, None, Millis(0))
            else:
                print("Failed to save character to file as backup!")
            raise e

    def _main_loop(self):
        while True:
            self.clock.tick()
            time_passed = Millis(self.clock.get_time())
            fps_string = str(int(self.clock.get_fps()))
            self.ui_view.update_fps_string(fps_string)

            input_events: List[Any] = pygame.event.get()
            for event in input_events:
                if event.type == pygame.QUIT:
                    self.quit_game()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.fullscreen:
                    self.toggle_fullscreen()
                    self.ui_view.on_fullscreen_changed(self.fullscreen)

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

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.pygame_screen = self.setup_screen()

    def setup_screen(self):
        flags = pygame.DOUBLEBUF
        if self.fullscreen:
            flags = flags | pygame.FULLSCREEN | pygame.HWSURFACE
        return pygame.display.set_mode(SCREEN_SIZE, flags)

    @staticmethod
    def quit_game():
        pygame.quit()
        sys.exit()

    def change_scene(self, scene_transition: SceneTransition):
        self.scene = scene_transition.scene
        self.scene.on_enter()


def start(map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
          start_money: Optional[int], save_file_name: Optional[str], fullscreen: bool):
    main = Main(map_file_name, chosen_hero_id, hero_start_level, start_money, save_file_name, fullscreen)
    main.main_loop()
