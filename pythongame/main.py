from typing import Optional, Dict

import pygame

from pythongame.core.common import SceneId, Millis, AbstractScene, SceneTransition
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, \
    UI_ICON_SPRITE_PATHS, PORTRAIT_ICON_SPRITE_PATHS
from pythongame.core.sound_player import init_sound_player
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.image_loading import load_images_by_sprite, \
    load_images_by_ui_sprite, load_images_by_portrait_sprite
from pythongame.register_game_data import register_all_game_data
from pythongame.scene_challenge_complete_screen.scene_challenge_complete_screen import ChallengeCompleteScreenScene
from pythongame.scene_creating_world.scene_creating_world import CreatingWorldScene
from pythongame.scene_picking_hero.scene_picking_hero import PickingHeroScene
from pythongame.scene_picking_hero.view_picking_hero import PickingHeroView
from pythongame.scene_starting_program.scene_starting_program import CommandlineFlags, StartingProgramScene
from pythongame.scene_victory_screen.scene_victory_screen import VictoryScreenScene
from pythongame.scenes_game.game_ui_view import GameUiView, UI_ICON_SIZE, PORTRAIT_ICON_SIZE, UI_ICON_BIG_SIZE
from pythongame.scenes_game.scene_paused import PausedScene
from pythongame.scenes_game.scene_playing import PlayingScene

SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 530)

register_all_game_data()


class Main:
    def __init__(self, map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
                 start_money: Optional[int], load_from_file: Optional[str]):

        cmd_flags = CommandlineFlags(map_file_name, chosen_hero_id, load_from_file, hero_start_level, start_money)

        pygame.init()

        pygame_screen = pygame.display.set_mode(SCREEN_SIZE)
        images_by_sprite = load_images_by_sprite(ENTITY_SPRITE_INITIALIZERS)
        images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_SIZE)
        big_images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, UI_ICON_BIG_SIZE)
        images_by_portrait_sprite = load_images_by_portrait_sprite(PORTRAIT_ICON_SPRITE_PATHS, PORTRAIT_ICON_SIZE)
        world_view = GameWorldView(pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite)
        self.ui_view = GameUiView(pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_ui_sprite, big_images_by_ui_sprite,
                                  images_by_portrait_sprite)
        init_sound_player()
        self.clock = pygame.time.Clock()
        self.scenes_by_id: Dict[SceneId, AbstractScene] = {
            SceneId.STARTING_PROGRAM: StartingProgramScene(),
            SceneId.PICKING_HERO: PickingHeroScene(PickingHeroView(pygame_screen, images_by_portrait_sprite)),
            SceneId.CREATING_GAME_WORLD: CreatingWorldScene(CAMERA_SIZE, self.ui_view),
            SceneId.PLAYING: PlayingScene(world_view),
            SceneId.PAUSED: PausedScene(world_view, self.ui_view),
            SceneId.VICTORY_SCREEN: VictoryScreenScene(pygame_screen),
            SceneId.CHALLENGE_COMPLETE_SCREEN: ChallengeCompleteScreenScene(pygame_screen)
        }
        self.scene_id = None
        self.transition_to_new_scene(SceneTransition(SceneId.STARTING_PROGRAM, cmd_flags))

    def main_loop(self):
        while True:
            self.clock.tick()
            time_passed = Millis(self.clock.get_time())
            fps_string = str(int(self.clock.get_fps()))
            self.ui_view.update_fps_string(fps_string)

            if self.scene_id in self.scenes_by_id:
                scene = self.scenes_by_id[self.scene_id]
                scene_transition: Optional[SceneTransition] = scene.run_one_frame(time_passed)
                if scene_transition is not None:
                    self.transition_to_new_scene(scene_transition)

            else:
                raise Exception("Unhandled scene: " + str(self.scene_id))

    def transition_to_new_scene(self, scene_transition: SceneTransition):
        print("transition: " + str(self.scene_id) + " --> " + str(scene_transition.scene_id) +
              " (" + str(scene_transition.data) + ")")
        self.scene_id = scene_transition.scene_id
        self.scenes_by_id[self.scene_id].initialize(scene_transition.data)


def start(map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
          start_money: Optional[int], load_from_file: Optional[str]):
    main = Main(map_file_name, chosen_hero_id, hero_start_level, start_money, load_from_file)
    main.main_loop()
