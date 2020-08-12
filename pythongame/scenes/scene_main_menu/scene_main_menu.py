from typing import List, Any, Optional

import pygame

from pythongame.core.common import AbstractScene, SceneTransition, Millis, SoundId
from pythongame.core.sound_player import play_sound
from pythongame.player_file import SavedPlayerState, SaveFileHandler
from pythongame.scenes.scene_creating_world.scene_creating_world import InitFlags
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scene_main_menu.view_main_menu import MainMenuView, NUM_SHOWN_SAVE_FILES

DIR_FONTS = './resources/fonts/'

COLOR_BLACK = (0, 0, 0)


class MainMenuScene(AbstractScene):
    def __init__(self,
                 save_file_handler: SaveFileHandler,
                 scene_factory: AbstractSceneFactory,
                 flags: InitFlags,
                 view: MainMenuView):
        self._selected_option_index = 0
        self._first_shown_option_index = 0
        self.scene_factory = scene_factory
        self.flags = flags
        self._files = save_file_handler.list_save_files()
        self._files.sort(key=lambda file: int(file.split(".")[0]))
        self._saved_characters: List[SavedPlayerState] = [
            save_file_handler.load_player_state_from_json_file(file) for file in self._files]
        self._view = view

    def handle_user_input(self, events: List[Any]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                    self._change_option(-1)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                    self._change_option(1)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self._confirm_option()

    def _change_option(self, delta: int):
        num_options = len(self._saved_characters) + 1
        self._selected_option_index = (self._selected_option_index + delta) % num_options

        if self._first_shown_option_index + NUM_SHOWN_SAVE_FILES <= self._selected_option_index \
                < len(self._saved_characters):
            self._first_shown_option_index = self._selected_option_index - NUM_SHOWN_SAVE_FILES + 1
        elif self._selected_option_index < self._first_shown_option_index:
            self._first_shown_option_index = self._selected_option_index

        play_sound(SoundId.DIALOG)

    def _confirm_option(self) -> Optional[SceneTransition]:
        if self._selected_option_index < len(self._saved_characters):
            self.flags.saved_player_state = self._saved_characters[self._selected_option_index]
            self.flags.character_file = self._files[self._selected_option_index]
            return SceneTransition(self.scene_factory.creating_world_scene(self.flags))
        else:
            return SceneTransition(self.scene_factory.picking_hero_scene(self.flags))

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:
        if not self._saved_characters:
            return SceneTransition(self.scene_factory.picking_hero_scene(self.flags))

    def render(self):
        self._view.render(self._saved_characters, self._selected_option_index, self._first_shown_option_index)
