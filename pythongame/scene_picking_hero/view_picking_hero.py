from typing import List, Dict, Any

import pygame
from pygame.rect import Rect

from pythongame.core.common import HeroId, PortraitIconSprite
from pythongame.core.game_data import HEROES
from pythongame.core.view.render_util import split_text_into_lines, DrawableArea

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
PORTRAIT_ICON_SIZE = (100, 70)

DIR_FONTS = './resources/fonts/'


class PickingHeroView:

    def __init__(self, pygame_screen, images_by_portrait_sprite: Dict[PortraitIconSprite, Any]):
        self.screen_size = pygame_screen.get_size()
        self.screen_render = DrawableArea(pygame_screen)
        self.font_large = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 32)
        self.font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.images_by_portrait_sprite = images_by_portrait_sprite

    def render(self, heroes: List[HeroId], selected_index: int):
        self.screen_render.fill(COLOR_BLACK)
        self.screen_render.rect(COLOR_WHITE, Rect(0, 0, self.screen_size[0], self.screen_size[1]), 1)
        y_0 = 200
        x_mid = self.screen_size[0] // 2
        x_base = x_mid - 175
        self.screen_render.text_centered(self.font_large, "SELECT HERO", (x_mid, y_0 - 100))
        for i, hero in enumerate(heroes):
            hero_data = HEROES[hero]
            sprite = hero_data.portrait_icon_sprite
            image = self.images_by_portrait_sprite[sprite]
            x = x_base + i * (PORTRAIT_ICON_SIZE[0] + 20)
            self.screen_render.image(image, (x, y_0))
            if i == selected_index:
                self.screen_render.rect(COLOR_HIGHLIGHTED_ICON,
                                        Rect(x, y_0, PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1]), 3)
            else:
                self.screen_render.rect(COLOR_WHITE, Rect(x, y_0, PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1]), 1)
            self.screen_render.text_centered(
                self.font, hero.name, (x + PORTRAIT_ICON_SIZE[0] // 2, y_0 + PORTRAIT_ICON_SIZE[1] + 10))
        description = HEROES[heroes[selected_index]].description
        description_lines = split_text_into_lines(description, 40)
        y_1 = 350
        for i, description_line in enumerate(description_lines):
            self.screen_render.text(self.font, description_line, (x_base - 8, y_1 + i * 20))

        y_2 = 500
        self.screen_render.text_centered(self.font, "Choose with arrow-keys", (x_mid, y_2))
        y_3 = 530
        self.screen_render.text_centered(self.font, "Press Space/Enter to confirm", (x_mid, y_3))
