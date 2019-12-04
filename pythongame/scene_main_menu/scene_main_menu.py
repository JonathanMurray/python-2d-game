from typing import List, Any, Callable, Optional

import pygame
from pygame.rect import Rect

from pythongame.core.common import AbstractScene, SceneTransition, Millis
from pythongame.core.view.render_util import DrawableArea
from pythongame.player_file import SavedPlayerState, SaveFileHandler
from pythongame.scene_creating_world.scene_creating_world import InitFlags

DIR_FONTS = './resources/fonts/'

COLOR_BLACK = (0, 0, 0)


class MainMenuScene(AbstractScene):
    def __init__(self, pygame_screen, save_file_handler: SaveFileHandler,
                 picking_hero_scene: Callable[[InitFlags], AbstractScene],
                 creating_world_scene: Callable[[InitFlags], AbstractScene], flags: InitFlags):
        self._screen_render = DrawableArea(pygame_screen)
        self._option_index = 0
        self._font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.picking_hero_scene = picking_hero_scene
        self.creating_world_scene = creating_world_scene
        self.flags = flags
        self._files = save_file_handler.list_save_files()
        self._saved_characters: List[SavedPlayerState] = [
            save_file_handler.load_player_state_from_json_file(file) for file in self._files]

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
        self._option_index = (self._option_index + delta) % num_options

    def _confirm_option(self) -> Optional[SceneTransition]:
        if self._option_index < len(self._saved_characters):
            self.flags.saved_player_state = self._saved_characters[self._option_index]
            self.flags.character_file = self._files[self._option_index]
            return SceneTransition(self.creating_world_scene(self.flags))
        else:
            return SceneTransition(self.picking_hero_scene(self.flags))

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:
        if not self._saved_characters:
            return SceneTransition(self.picking_hero_scene(self.flags))

    def render(self):
        self._screen_render.fill(COLOR_BLACK)
        x = 200
        y = 100

        if len(self._saved_characters) == 1:
            text = "You have 1 character"
        else:
            text = "You have " + str(len(self._saved_characters)) + " characters"
        self._screen_render.text(self._font, text, (x, y))
        y += 100

        color_rect = (150, 150, 250)
        color_highlighted = (250, 250, 250)
        for i, saved_player_state in enumerate(self._saved_characters):
            color = color_highlighted if i == self._option_index else color_rect
            self._screen_render.rect(color, Rect(x, y, 200, 70), 2)
            text = saved_player_state.hero_id + " LEVEL " + str(saved_player_state.level)
            self._screen_render.text(self._font, text, (x + 10, y + 14))
            text_2 = "PLAYED TIME: " + _get_time_str(saved_player_state.total_time_played_on_character)
            y += 25
            self._screen_render.text(self._font, text_2, (x + 10, y + 14))
            y += 80

        y += 10
        color = color_highlighted if self._option_index == len(self._saved_characters) else color_rect
        self._screen_render.rect(color, Rect(x, y, 200, 50), 2)
        self._screen_render.text(self._font, "CREATE NEW CHARACTER", (x + 10, y + 14))


def _get_time_str(millis):
    seconds = millis // 1_000
    if seconds < 60:
        return str(seconds) + "s"
    if seconds == 60:
        return "1min"
    minutes = seconds // 60
    if minutes < 10:
        seconds_remainder = seconds - minutes * 60
        return str(minutes) + "min " + str(seconds_remainder) + "s"
    if minutes < 60:
        return str(minutes) + "min"
    if minutes == 60:
        return "1h"
    hours = minutes // 60
    minutes_remainder = minutes - hours * 60
    return str(hours) + "h " + str(minutes_remainder) + "min"
