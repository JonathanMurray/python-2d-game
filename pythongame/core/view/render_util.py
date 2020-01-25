from typing import Tuple, Callable, List, Optional

import pygame
from pygame.rect import Rect

from pythongame.core.math import sum_of_vectors
from pythongame.core.view.image_loading import ImageWithRelativePosition

COLOR_WHITE = (250, 250, 250)


class DrawableArea:
    def __init__(self, screen, translate_coordinates: Callable[[Tuple[int, int]], Tuple[int, int]] = lambda pos: pos):
        self.screen = screen
        self.translate_coordinates = translate_coordinates

    def fill(self, color: Tuple[int, int, int]):
        self.screen.fill(color)

    def rect(self, color: Tuple[int, int, int], rect: Rect, line_width: int):
        pygame.draw.rect(self.screen, color, self._translate_rect(rect), line_width)

    def rect_filled(self, color: Tuple[int, int, int], rect: Rect):
        pygame.draw.rect(self.screen, color, self._translate_rect(rect))

    def rect_transparent(self, rect: Rect, alpha: int, color):
        # Using a separate surface is the only way to render a transparent rectangle
        surface = pygame.Surface((rect[2], rect[3]))
        surface.set_alpha(alpha)
        surface.fill(color)
        self.screen.blit(surface, self._translate_pos((rect[0], rect[1])))

    def line(self, color, start_pos: Tuple[int, int], end_pos: Tuple[int, int], line_width: int):
        pygame.draw.line(self.screen, color, self._translate_pos(start_pos), self._translate_pos(end_pos), line_width)

    def circle(self, color, pos: Tuple[int, int], radius: int, line_width: int):
        pygame.draw.circle(self.screen, color, self._translate_pos(pos), radius, line_width)

    def stat_bar(self, x: int, y: int, w: int, h: int, ratio_filled: float, color,
                 border_color: Optional[Tuple[int, int, int]] = None):
        self.rect_filled((0, 0, 0), Rect(x - 1, y - 1, w + 2, h + 2))
        if border_color:
            self.rect(border_color, Rect(x - 2, y - 2, w + 4, h + 4), 1)
        self.rect_filled(color, Rect(x, y, max(w * ratio_filled, 0), h))

    def text(self, font, text: str, pos: Tuple[int, int], color=COLOR_WHITE):
        self.screen.blit(font.render(text, True, color), self._translate_pos(pos))

    def text_centered(self, font, text: str, center_pos: Tuple[int, int], color=COLOR_WHITE):
        width = font.size(text)[0]
        pos = (int(center_pos[0] - width / 2), center_pos[1])
        self.text(font, text, pos, color)

    def image(self, image, pos: Tuple[int, int]):
        self.screen.blit(image, self._translate_pos(pos))

    def image_with_relative_pos(self, image_with_relative_position: ImageWithRelativePosition, pos: Tuple[int, int]):
        translated_pos = sum_of_vectors(pos, image_with_relative_position.position_relative_to_entity)
        self.image(image_with_relative_position.image, translated_pos)

    def _translate_rect(self, rect: Rect):
        translated_pos = self.translate_coordinates((rect[0], rect[1]))
        translated_rect = (translated_pos[0], translated_pos[1], rect[2], rect[3])
        return translated_rect

    def _translate_pos(self, pos: Tuple[int, int]):
        return self.translate_coordinates((pos[0], pos[1]))


def split_text_into_lines(full_text: str, max_line_length: int) -> List[str]:
    if len(full_text) == 0:
        return []
    tokens = full_text.split()
    lines = []
    line = tokens[0]
    for token in tokens[1:]:
        if len(line + ' ' + token) <= max_line_length:
            line = line + ' ' + token
        else:
            lines.append(line)
            line = token
    lines.append(line)
    return lines
