from enum import Enum
from typing import Any
from typing import Dict, List, Tuple, Optional

import pygame
from pygame.rect import Rect

from pythongame.core.common import Direction, Sprite, UiIconSprite
from pythongame.core.common import PortraitIconSprite
from pythongame.core.game_data import ITEMS, CONSUMABLES
from pythongame.core.item_inventory import ITEM_EQUIPMENT_CATEGORY_NAMES
from pythongame.core.math import sum_of_vectors
from pythongame.core.view.image_loading import ImageWithRelativePosition
from pythongame.core.view.render_util import DrawableArea
from pythongame.map_editor.map_editor_world_entity import MapEditorWorldEntity
from pythongame.scenes_game.ui_components import RadioButton, Checkbox, Button, Minimap, MapEditorIcon, TooltipGraphics

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
PORTRAIT_ICON_SIZE = (100, 70)

RENDER_WORLD_COORDINATES = False

DIR_FONTS = './resources/fonts/'

MAP_EDITOR_UI_ICON_SIZE = (32, 32)


class EntityTab(Enum):
    ITEMS = 0
    NPCS = 1
    WALLS = 2
    MISC = 3


class GenerateRandomMap:
    pass


class SetCameraPosition:
    def __init__(self, position_ratio: Tuple[float, float]):
        self.position_ratio = position_ratio


class EnableEntityTab:
    def __init__(self, entity_tab: EntityTab):
        self.entity_tab = entity_tab


class MapEditorView:

    def __init__(self,
                 pygame_screen,
                 camera_size: Tuple[int, int],
                 screen_size: Tuple[int, int],
                 images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]],
                 images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any],
                 world_area: Rect,
                 player_position: Tuple[int, int],
                 entities_by_type: Dict[EntityTab, List[MapEditorWorldEntity]]):
        self.camera_size = camera_size
        self.screen_size = screen_size
        self.screen_render = DrawableArea(pygame_screen)

        self.images_by_sprite = images_by_sprite
        self.images_by_ui_sprite = images_by_ui_sprite
        self.images_by_portrait_sprite = images_by_portrait_sprite
        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)

        self.font_debug_info = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        w_tab_button = 75
        self.tab_buttons_by_entity_type = {
            EntityTab.ITEMS: RadioButton(self.ui_render, Rect(300, 10, w_tab_button, 20), "ITEMS (V)"),
            EntityTab.NPCS: RadioButton(self.ui_render, Rect(380, 10, w_tab_button, 20), "NPCS (B)"),
            EntityTab.WALLS: RadioButton(self.ui_render, Rect(460, 10, w_tab_button, 20), "WALLS (N)"),
            EntityTab.MISC: RadioButton(self.ui_render, Rect(540, 10, w_tab_button, 20), "MISC. (M)"),
        }
        self.entities_by_type = entities_by_type
        self.tab_buttons = list(self.tab_buttons_by_entity_type.values())
        self.minimap = Minimap(self.ui_render, Rect(self.screen_size[0] - 180, 20, 160, 160), world_area,
                               player_position)
        self.shown_tab: EntityTab = None
        self.set_shown_tab(EntityTab.ITEMS)
        self.checkbox_show_entity_outlines = Checkbox(self.ui_render, Rect(15, 100, 120, 20), "outlines", False)
        self.checkboxes = [self.checkbox_show_entity_outlines]
        self.button_generate_random_map: Button = Button(self.ui_render, Rect(15, 125, 120, 20), "generate random")
        self.mouse_screen_position = (0, 0)
        self.hovered_component = None
        self._setup_ui_components()

    def _setup_ui_components(self):
        icon_space = 5
        x_1 = 155
        y_2 = 40
        self.button_delete_entities = self._map_editor_icon_in_ui(
            Rect(20, y_2, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1]),
            'Q', None, UiIconSprite.MAP_EDITOR_TRASHCAN, 0, None)
        self.button_delete_decorations = self._map_editor_icon_in_ui(
            Rect(20 + MAP_EDITOR_UI_ICON_SIZE[0] + icon_space, y_2, MAP_EDITOR_UI_ICON_SIZE[0],
                 MAP_EDITOR_UI_ICON_SIZE[1]), 'Z', None, UiIconSprite.MAP_EDITOR_RECYCLING, 0, None)
        self.entity_icons_by_type = {}
        num_icons_per_row = 23
        for entity_type in EntityTab:
            self.entity_icons_by_type[entity_type] = []
            for i, entity in enumerate(self.entities_by_type[entity_type]):
                x = x_1 + (i % num_icons_per_row) * (MAP_EDITOR_UI_ICON_SIZE[0] + icon_space)
                row_index = (i // num_icons_per_row)
                y = y_2 + row_index * (MAP_EDITOR_UI_ICON_SIZE[1] + icon_space)
                if entity.item_type is not None:
                    data = ITEMS[entity.item_type]
                    category_name = None
                    if data.item_equipment_category:
                        category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[data.item_equipment_category]
                    tooltip = TooltipGraphics.create_for_item(self.ui_render, data, category_name, (x, y))
                elif entity.consumable_type is not None:
                    data = CONSUMABLES[entity.consumable_type]
                    tooltip = TooltipGraphics.create_for_consumable(self.ui_render, data, (x, y))
                else:
                    tooltip = None
                icon = self._map_editor_icon_in_ui(
                    Rect(x, y, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1]), '', entity.sprite, None,
                    entity.map_editor_entity_id, tooltip)
                self.entity_icons_by_type[entity_type].append(icon)

    def handle_mouse_movement(self, mouse_screen_pos: Tuple[int, int]) -> Optional[MapEditorWorldEntity]:
        self.mouse_screen_position = mouse_screen_pos

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_pos)

        for icon in self.entity_icons_by_type[self.shown_tab]:
            if icon.contains(mouse_ui_position):
                self._on_hover_component(icon)
                entity = [e for e in self.entities_by_type[self.shown_tab]
                          if e.map_editor_entity_id == icon.map_editor_entity_id][0]
                return entity

        for component in self.checkboxes + [self.button_generate_random_map, self.minimap] + self.tab_buttons:
            if component.contains(mouse_ui_position):
                self._on_hover_component(component)
                return None

        # If something was hovered, we would have returned from the method
        self._set_currently_hovered_component_not_hovered()

    def _on_hover_component(self, component):
        self._set_currently_hovered_component_not_hovered()
        self.hovered_component = component
        self.hovered_component.hovered = True

    def _set_currently_hovered_component_not_hovered(self):
        if self.hovered_component is not None:
            self.hovered_component.hovered = False
            self.hovered_component = None

    def handle_mouse_click(self) -> Optional[Any]:
        if self.hovered_component in self.checkboxes:
            self.hovered_component.on_click()
            return None
        if self.hovered_component == self.button_generate_random_map:
            return GenerateRandomMap()
        if self.hovered_component == self.minimap:
            mouse_ui_position = self._translate_screen_position_to_ui(self.mouse_screen_position)
            position_ratio = self.minimap.get_position_ratio(mouse_ui_position)
            return SetCameraPosition(position_ratio)
        for entity_type in self.tab_buttons_by_entity_type:
            if self.hovered_component == self.tab_buttons_by_entity_type[entity_type]:
                self.set_shown_tab(entity_type)
                return EnableEntityTab(entity_type)

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

    def set_shown_tab(self, shown_tab: EntityTab):
        if self.shown_tab:
            self.tab_buttons_by_entity_type[self.shown_tab].enabled = False
        self.shown_tab = shown_tab
        self.tab_buttons_by_entity_type[shown_tab].enabled = True

    def render(
            self,
            placing_entity: Optional[MapEditorWorldEntity],
            deleting_entities: bool,
            deleting_decorations: bool,
            num_enemies: int,
            num_walls: int,
            num_decorations: int,
            grid_cell_size: int,
            camera_world_area: Rect,
            npc_positions: List[Tuple[int, int]],
            wall_positions: List[Tuple[int, int]],
            player_position: Tuple[int, int],
            world_area: Rect):

        self.screen_render.rect(COLOR_BLACK, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self.screen_render.rect_filled(COLOR_BLACK, Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        self.button_delete_entities.render(deleting_entities)
        self.button_delete_decorations.render(deleting_decorations)

        for icon in self.entity_icons_by_type[self.shown_tab]:
            highlighted = placing_entity and placing_entity.map_editor_entity_id == icon.map_editor_entity_id
            icon.render(highlighted)

        self.screen_render.rect(COLOR_WHITE, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 150, 80), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, "# enemies: " + str(num_enemies), (5, 3))
        self.screen_render.text(self.font_debug_info, "# walls: " + str(num_walls), (5, 20))
        self.screen_render.text(self.font_debug_info, "# decorations: " + str(num_decorations), (5, 37))
        self.screen_render.text(self.font_debug_info, "Cell size: " + str(grid_cell_size), (5, 54))

        self.minimap.set_walls(wall_positions)
        self.minimap.update_camera_area(camera_world_area)
        self.minimap.update_npc_positions(npc_positions)
        self.minimap.update_player_position(player_position)
        self.minimap.update_world_area(world_area)
        self.minimap.render()

        for checkbox in self.checkboxes + self.tab_buttons:
            checkbox.render()

        self.button_generate_random_map.render()

        if self.hovered_component and self.hovered_component.tooltip:
            tooltip: TooltipGraphics = self.hovered_component.tooltip
            tooltip.render()

    def render_map_editor_mouse_rect(self, color: Tuple[int, int, int], map_editor_mouse_rect: Rect):
        self.screen_render.rect(color, map_editor_mouse_rect, 3)

    def render_map_editor_world_entity_at_position(self, sprite: Sprite, entity_size: Tuple[int, int],
                                                   position: Tuple[int, int]):
        image_with_relative_position = self._get_image_for_sprite(sprite, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self.screen_render.image(image_with_relative_position.image, sprite_position)
        self.screen_render.rect((50, 250, 0), Rect(position[0], position[1], entity_size[0], entity_size[1]), 3)

    def _map_editor_icon_in_ui(self, rect: Rect, user_input_key: str,
                               sprite: Optional[Sprite], ui_icon_sprite: Optional[UiIconSprite],
                               map_editor_entity_id: int, tooltip: TooltipGraphics) -> MapEditorIcon:
        if sprite:
            image = self.images_by_sprite[sprite][Direction.DOWN][0].image
        elif ui_icon_sprite:
            image = self.images_by_ui_sprite[ui_icon_sprite]
        else:
            raise Exception("Nothing to render!")

        return MapEditorIcon(self.ui_render, rect, image, self.font_ui_icon_keys, user_input_key, map_editor_entity_id,
                             tooltip)

    def is_screen_position_within_ui(self, screen_position: Tuple[int, int]):
        ui_position = self._translate_screen_position_to_ui(screen_position)
        return ui_position[1] >= 0
