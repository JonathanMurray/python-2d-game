from typing import Dict, Any, List

import pygame
from pygame.rect import Rect

from pythongame.core.common import PortraitIconSprite, HeroId
from pythongame.core.game_data import HEROES, HeroData
from pythongame.core.view.render_util import DrawableArea
from pythongame.player_file import SavedPlayerState

NUM_SHOWN_SAVE_FILES = 3

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)

COLOR_RECT = (70, 70, 70)
COLOR_HIGHLIGHTED_RECT = (250, 250, 150)
PORTRAIT_ICON_SIZE = (100, 70)

DIR_FONTS = './resources/fonts/'


class MainMenuView:

    def __init__(self, pygame_screen, images_by_portrait_sprite: Dict[PortraitIconSprite, Any]):
        self._screen_size = pygame_screen.get_size()
        self._screen_render = DrawableArea(pygame_screen)
        self._font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self._images_by_portrait_sprite = images_by_portrait_sprite

    def render(self, saved_characters: List[SavedPlayerState], selected_option_index: int, first_shown_index: int):
        self._screen_render.fill(COLOR_BLACK)
        self._screen_render.rect(COLOR_WHITE, Rect(0, 0, self._screen_size[0], self._screen_size[1]), 1)
        x_mid = self._screen_size[0] // 2
        x = x_mid - 175
        x_text = x + PORTRAIT_ICON_SIZE[0] + 25
        y = 50

        if len(saved_characters) == 1:
            top_text = "You have 1 saved character"
        else:
            top_text = "You have " + str(len(saved_characters)) + " saved characters"
        self._screen_render.text_centered(self._font, top_text, (x_mid, y))
        y += 100

        w_rect = 340
        h_rect = 80
        padding = 5
        for i in range(first_shown_index, min(len(saved_characters), first_shown_index + NUM_SHOWN_SAVE_FILES)):
            saved_player_state = saved_characters[i]
            color = COLOR_HIGHLIGHTED_RECT if i == selected_option_index else COLOR_RECT
            self._screen_render.rect(color, Rect(x, y, w_rect, h_rect), 2)
            image = self._get_portrait_image(saved_player_state)
            self._screen_render.image(image, (x + padding, y + padding))
            self._screen_render.rect(
                COLOR_WHITE, Rect(x + padding, y + padding, PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1]), 1)
            text_1 = saved_player_state.hero_id + " LEVEL " + str(saved_player_state.level)

            self._screen_render.text(self._font, text_1, (x_text, y + 20))
            text_2 = "played time: " + _get_time_str(saved_player_state.total_time_played_on_character)
            self._screen_render.text(self._font, text_2, (x_text, y + 45))
            y += 90

        y += 40
        color = COLOR_HIGHLIGHTED_RECT if selected_option_index == len(saved_characters) else COLOR_RECT
        self._screen_render.rect(color, Rect(x, y, w_rect, h_rect), 2)
        self._screen_render.text_centered(self._font, "CREATE NEW CHARACTER", (x_mid, y + 32))

    def _get_portrait_image(self, saved_player_state):
        hero_data: HeroData = HEROES[HeroId[saved_player_state.hero_id]]
        sprite = hero_data.portrait_icon_sprite
        image = self._images_by_portrait_sprite[sprite]
        return image


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
