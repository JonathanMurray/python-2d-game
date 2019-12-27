from typing import Optional

import pygame

from pythongame.core.common import Millis, AbstractScene, SceneTransition
from pythongame.core.view.render_util import DrawableArea

COLOR_BLACK = (0, 0, 0)
DIR_FONTS = './resources/fonts/'


def get_time_str(millis: Millis):
    if millis < 60_000:
        return str(millis // 1_000) + " seconds"
    if millis < 120_000:
        return "1 minute and " + str((millis - 60_000) // 1_000) + " seconds"
    return str(millis // 60_000) + " minutes"


class ChallengeCompleteScreenScene(AbstractScene):
    def __init__(self, pygame_screen, total_time_played: Millis):
        self.screen_size = pygame_screen.get_size()
        self.screen_render = DrawableArea(pygame_screen)
        self.font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.time_since_start = Millis(0)
        self.total_time_played = total_time_played

    def run_one_frame(self, time_passed: Millis) -> Optional[SceneTransition]:
        self.time_since_start += time_passed
        return None

    def render(self):
        self.screen_render.fill(COLOR_BLACK)
        x_mid = self.screen_size[0] // 2
        x = x_mid - 280
        lines_y = [200,
                   325, 350,
                   500, 525, 550]
        text_lines = ["            Challenge completed in " + get_time_str(self.total_time_played) + "!"]

        num_chars_to_show = self.time_since_start // 30
        accumulated = 0
        for i in range(len(text_lines)):
            if num_chars_to_show > accumulated:
                line = text_lines[i]
                self.screen_render.text(self.font, line[:num_chars_to_show - accumulated], (x, lines_y[i]))
                accumulated += len(line)
