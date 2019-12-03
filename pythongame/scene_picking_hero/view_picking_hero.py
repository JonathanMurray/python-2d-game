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
        self.screen_render = DrawableArea(pygame_screen)
        self.font = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.images_by_portrait_sprite = images_by_portrait_sprite

    def render(self, heroes: List[HeroId], selected_index: int):
        self.screen_render.fill(COLOR_BLACK)
        x_base = 170
        y_0 = 200
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
            self.screen_render.text(self.font, hero.name, (x, y_0 + PORTRAIT_ICON_SIZE[1] + 10))
        description = HEROES[heroes[selected_index]].description
        description_lines = split_text_into_lines(description, 40)
        y_1 = 350
        for i, description_line in enumerate(description_lines):
            self.screen_render.text(self.font, description_line, (x_base, y_1 + i * 20))
        y_2 = 500
        self.screen_render.text(self.font, "SELECT YOUR HERO (Space to confirm)", (x_base, y_2))
