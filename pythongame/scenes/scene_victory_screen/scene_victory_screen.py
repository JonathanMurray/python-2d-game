from typing import Optional

import pygame

from pythongame.core.common import Millis, AbstractScene, SceneTransition
from pythongame.core.view.render_util import DrawableArea

COLOR_BLACK = (0, 0, 0)
DIR_FONTS = './resources/fonts/'


class VictoryScreenScene(AbstractScene):
    def __init__(self, pygame_screen):
        self.screen_size = pygame_screen.get_size()
        self.screen_render = DrawableArea(pygame_screen)
        self.font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.time_since_start = Millis(0)

    def run_one_frame(self, time_passed: Millis) -> Optional[SceneTransition]:
        self.time_since_start += time_passed
        return None

    def render(self):
        self.screen_render.fill(COLOR_BLACK)
        x_mid = self.screen_size[0] // 2
        x = x_mid - 280
        lines_y = [150,
                   275, 300,
                   450, 475, 500]
        text_lines = [
            " Well done! You have finished the demo version of this game!",

            "           Don't hesitate to drop any feedback at",
            "   https://github.com/JonathanMurray/python-2d-game/issues  ",

            "                      /",
            "                  O===[====================-",
            "                      \\"
        ]

        num_chars_to_show = self.time_since_start // 30
        accumulated = 0
        for i in range(len(text_lines)):
            if num_chars_to_show > accumulated:
                line = text_lines[i]
                self.screen_render.text(self.font, line[:num_chars_to_show - accumulated], (x, lines_y[i]))
                accumulated += len(line)
