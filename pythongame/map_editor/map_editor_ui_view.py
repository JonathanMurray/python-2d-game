from typing import Any
from typing import Dict, List, Tuple, Optional

import pygame
from pygame.rect import Rect

from pythongame.core.common import Direction, Sprite, UiIconSprite
from pythongame.core.common import PortraitIconSprite
from pythongame.core.math import is_point_in_rect, sum_of_vectors
from pythongame.core.view.image_loading import ImageWithRelativePosition
from pythongame.core.view.render_util import DrawableArea
from pythongame.map_editor.map_editor_world_entity import MapEditorWorldEntity

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
PORTRAIT_ICON_SIZE = (100, 70)

RENDER_WORLD_COORDINATES = False

DIR_FONTS = './resources/fonts/'

MAP_EDITOR_UI_ICON_SIZE = (32, 32)


class MapEditorView:

    def __init__(self, pygame_screen, camera_size: Tuple[int, int], screen_size: Tuple[int, int],
                 images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]],
                 images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any]):
        self.camera_size = camera_size
        self.screen_size = screen_size
        self.screen_render = DrawableArea(pygame_screen)

        self.images_by_sprite = images_by_sprite
        self.images_by_ui_sprite = images_by_ui_sprite
        self.images_by_portrait_sprite = images_by_portrait_sprite
        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)

        self.font_ui_headers = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 18)
        self.font_debug_info = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    def _get_image_for_sprite(self, sprite: Sprite, direction: Direction,
                              animation_progress: float) -> ImageWithRelativePosition:

        images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[sprite]
        if direction in images:
            images_for_this_direction = images[direction]
        else:
            images_for_this_direction = next(iter(images.values()))

        animation_frame_index = int(len(images_for_this_direction) * animation_progress)
        return images_for_this_direction[animation_frame_index]

    def render(
            self, chars_by_entities: Dict[MapEditorWorldEntity, str], entities: List[MapEditorWorldEntity],
            placing_entity: Optional[MapEditorWorldEntity], deleting_entities: bool, deleting_decorations: bool,
            num_enemies: int, num_walls: int, num_decorations: int, grid_cell_size: int,
            mouse_screen_position: Tuple[int, int]) -> Optional[MapEditorWorldEntity]:

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)

        hovered_by_mouse: MapEditorWorldEntity = None

        self.screen_render.rect(COLOR_BLACK, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self.screen_render.rect_filled(COLOR_BLACK, Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        icon_space = 5

        y_1 = 17
        y_2 = y_1 + 22

        x_0 = 20
        self._map_editor_icon_in_ui(x_0, y_2, MAP_EDITOR_UI_ICON_SIZE, deleting_entities, 'Q', None,
                                    UiIconSprite.MAP_EDITOR_TRASHCAN)
        self._map_editor_icon_in_ui(x_0 + MAP_EDITOR_UI_ICON_SIZE[0] + icon_space, y_2, MAP_EDITOR_UI_ICON_SIZE,
                                    deleting_decorations, 'Z', None, UiIconSprite.MAP_EDITOR_RECYCLING)

        x_1 = 155
        self.ui_render.text(self.font_ui_headers, "ENTITIES", (x_1, y_1))
        num_icons_per_row = 27
        for i, entity in enumerate(entities):
            if entity in chars_by_entities:
                char = chars_by_entities[entity]
            else:
                char = ''
            is_this_entity_being_placed = entity is placing_entity
            x = x_1 + (i % num_icons_per_row) * (MAP_EDITOR_UI_ICON_SIZE[0] + icon_space)
            row_index = (i // num_icons_per_row)
            y = y_2 + row_index * (MAP_EDITOR_UI_ICON_SIZE[1] + 25)
            if is_point_in_rect(mouse_ui_position, Rect(x, y, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1])):
                hovered_by_mouse = entity
            self._map_editor_icon_in_ui(
                x, y, MAP_EDITOR_UI_ICON_SIZE, is_this_entity_being_placed, char, entity.sprite, None)

        self.screen_render.rect(COLOR_WHITE, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 150, 80), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, "# enemies: " + str(num_enemies), (5, 3))
        self.screen_render.text(self.font_debug_info, "# walls: " + str(num_walls), (5, 20))
        self.screen_render.text(self.font_debug_info, "# decorations: " + str(num_decorations), (5, 37))
        self.screen_render.text(self.font_debug_info, "Cell size: " + str(grid_cell_size), (5, 54))

        return hovered_by_mouse

    def render_map_editor_mouse_rect(self, color: Tuple[int, int, int], map_editor_mouse_rect: Rect):
        self.screen_render.rect(color, map_editor_mouse_rect, 3)

    def render_map_editor_world_entity_at_position(self, sprite: Sprite, entity_size: Tuple[int, int],
                                                   position: Tuple[int, int]):
        image_with_relative_position = self._get_image_for_sprite(sprite, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self.screen_render.image(image_with_relative_position.image, sprite_position)
        self.screen_render.rect((50, 250, 0), Rect(position[0], position[1], entity_size[0], entity_size[1]), 3)

    def _map_editor_icon_in_ui(self, x, y, size: Tuple[int, int], highlighted: bool, user_input_key: str,
                               sprite: Optional[Sprite], ui_icon_sprite: Optional[UiIconSprite]):
        w = size[0]
        h = size[1]
        self.ui_render.rect_filled((40, 40, 40), Rect(x, y, w, h))
        if sprite:
            image = self.images_by_sprite[sprite][Direction.DOWN][0].image
        elif ui_icon_sprite:
            image = self.images_by_ui_sprite[ui_icon_sprite]
        else:
            raise Exception("Nothing to render!")

        icon_scaled_image = pygame.transform.scale(image, size)
        self.ui_render.image(icon_scaled_image, (x, y))

        self.ui_render.rect(COLOR_WHITE, Rect(x, y, w, h), 2)
        if highlighted:
            self.ui_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        self.ui_render.text(self.font_ui_icon_keys, user_input_key, (x + 12, y + h + 4))

    def is_screen_position_within_ui(self, screen_position: Tuple[int, int]):
        ui_position = self._translate_screen_position_to_ui(screen_position)
        return ui_position[1] >= 0
