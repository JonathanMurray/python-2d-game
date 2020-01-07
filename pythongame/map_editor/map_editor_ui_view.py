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
from pythongame.scenes_game.ui_components import RadioButton, Checkbox, Button, Minimap, MapEditorIcon, TooltipGraphics, \
    UiComponent

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


class MapEditorAction:
    pass


class AddEntity(MapEditorAction):
    def __init__(self, world_position: Tuple[int, int], entity: MapEditorWorldEntity):
        self.world_position = world_position
        self.entity = entity


class DeleteEntities(MapEditorAction):
    def __init__(self, world_position: Tuple[int, int]):
        self.world_position = world_position


class DeleteDecorations(MapEditorAction):
    def __init__(self, world_position: Tuple[int, int]):
        self.world_position = world_position


class SetPlayerPosition(MapEditorAction):
    def __init__(self, world_position: Tuple[int, int]):
        self.world_position = world_position


class GenerateRandomMap(MapEditorAction):
    pass


class SaveMap(MapEditorAction):
    pass


class SetCameraPosition(MapEditorAction):
    def __init__(self, position_ratio: Tuple[float, float]):
        self.position_ratio = position_ratio


class UserState:
    def __init__(self, placing_entity: Optional[MapEditorWorldEntity], deleting_entities: bool,
                 deleting_decorations: bool):
        self.placing_entity = placing_entity
        self.deleting_entities = deleting_entities
        self.deleting_decorations = deleting_decorations

    @staticmethod
    def placing_entity(entity: MapEditorWorldEntity):
        return UserState(entity, False, False)

    @staticmethod
    def deleting_entities():
        return UserState(None, True, False)

    @staticmethod
    def deleting_decorations():
        return UserState(None, False, True)


class MapEditorView:

    def __init__(self,
                 pygame_screen,
                 camera_world_area: Rect,
                 screen_size: Tuple[int, int],
                 images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]],
                 images_by_ui_sprite: Dict[UiIconSprite, Any],
                 images_by_portrait_sprite: Dict[PortraitIconSprite, Any],
                 world_area: Rect,
                 player_position: Tuple[int, int],
                 entities_by_type: Dict[EntityTab, List[MapEditorWorldEntity]],
                 grid_cell_size: int):
        camera_size = camera_world_area.size
        self._camera_size = camera_size
        self._screen_size = screen_size
        self._screen_render = DrawableArea(pygame_screen)

        self._images_by_sprite = images_by_sprite
        self._images_by_ui_sprite = images_by_ui_sprite
        self._images_by_portrait_sprite = images_by_portrait_sprite
        self._ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self._screen_render = DrawableArea(pygame_screen)
        self._ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)

        self._font_debug_info = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self._font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        w_tab_button = 75
        self._tab_buttons_by_entity_type = {
            EntityTab.ITEMS: RadioButton(self._ui_render, Rect(300, 10, w_tab_button, 20), "ITEMS (V)"),
            EntityTab.NPCS: RadioButton(self._ui_render, Rect(380, 10, w_tab_button, 20), "NPCS (B)"),
            EntityTab.WALLS: RadioButton(self._ui_render, Rect(460, 10, w_tab_button, 20), "WALLS (N)"),
            EntityTab.MISC: RadioButton(self._ui_render, Rect(540, 10, w_tab_button, 20), "MISC. (M)"),
        }
        self._entities_by_type = entities_by_type
        self._tab_buttons = list(self._tab_buttons_by_entity_type.values())
        self._minimap = Minimap(self._ui_render, Rect(self._screen_size[0] - 180, 20, 160, 160), world_area,
                                player_position)
        self._shown_tab: EntityTab = None
        self._set_shown_tab(EntityTab.ITEMS)
        self._checkbox_show_entity_outlines = Checkbox(self._ui_render, Rect(15, 100, 120, 20), "outlines", False)
        self._checkboxes = [self._checkbox_show_entity_outlines]
        self._button_generate_random_map: Button = Button(self._ui_render, Rect(15, 125, 120, 20), "generate random")
        self._button_save: Button = Button(self._ui_render, Rect(15, 155, 120, 20), "save")
        self._buttons = [self._button_generate_random_map, self._button_save]

        # USER INPUT STATE
        self._is_mouse_button_down = False
        self._mouse_screen_pos = (0, 0)
        self._hovered_component = None
        self._user_state = UserState.deleting_entities()
        self._snapped_mouse_screen_pos = (0, 0)
        self._snapped_mouse_world_pos = (0, 0)
        self._is_snapped_mouse_within_world = True
        self._is_snapped_mouse_over_ui = False
        self._entity_icon_hovered_by_mouse = None

        # MUTABLE WORLD-RELATED STATE
        self.camera_world_area: Rect = camera_world_area
        self.world_area: Rect = world_area
        self.grid_cell_size = grid_cell_size

        self._setup_ui_components()

    def _setup_ui_components(self):
        icon_space = 5
        x_1 = 155
        y_2 = 40
        self.button_delete_entities = self._create_map_editor_icon(
            Rect(20, y_2, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1]),
            'Q', None, UiIconSprite.MAP_EDITOR_TRASHCAN, 0, None)
        self.button_delete_decorations = self._create_map_editor_icon(
            Rect(20 + MAP_EDITOR_UI_ICON_SIZE[0] + icon_space, y_2, MAP_EDITOR_UI_ICON_SIZE[0],
                 MAP_EDITOR_UI_ICON_SIZE[1]), 'Z', None, UiIconSprite.MAP_EDITOR_RECYCLING, 0, None)
        self.entity_icons_by_type = {}
        num_icons_per_row = 23
        for entity_type in EntityTab:
            self.entity_icons_by_type[entity_type] = []
            for i, entity in enumerate(self._entities_by_type[entity_type]):
                x = x_1 + (i % num_icons_per_row) * (MAP_EDITOR_UI_ICON_SIZE[0] + icon_space)
                row_index = (i // num_icons_per_row)
                y = y_2 + row_index * (MAP_EDITOR_UI_ICON_SIZE[1] + icon_space)
                if entity.item_type is not None:
                    data = ITEMS[entity.item_type]
                    category_name = None
                    if data.item_equipment_category:
                        category_name = ITEM_EQUIPMENT_CATEGORY_NAMES[data.item_equipment_category]
                    tooltip = TooltipGraphics.create_for_item(self._ui_render, data, category_name, (x, y))
                elif entity.consumable_type is not None:
                    data = CONSUMABLES[entity.consumable_type]
                    tooltip = TooltipGraphics.create_for_consumable(self._ui_render, data, (x, y))
                else:
                    tooltip = None
                icon = self._create_map_editor_icon(
                    Rect(x, y, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1]), '', entity.sprite, None,
                    entity.map_editor_entity_id, tooltip)
                self.entity_icons_by_type[entity_type].append(icon)

    # HANDLE USER INPUT

    def handle_mouse_movement(self, mouse_screen_pos: Tuple[int, int]) -> Optional[MapEditorAction]:
        self._mouse_screen_pos = mouse_screen_pos
        self._entity_icon_hovered_by_mouse = None

        self._snapped_mouse_screen_pos = ((mouse_screen_pos[0] // self.grid_cell_size) * self.grid_cell_size,
                                          (mouse_screen_pos[1] // self.grid_cell_size) * self.grid_cell_size)
        self._snapped_mouse_world_pos = sum_of_vectors(self._snapped_mouse_screen_pos,
                                                       self.camera_world_area.topleft)
        self._is_snapped_mouse_within_world = self.world_area.collidepoint(self._snapped_mouse_world_pos[0],
                                                                           self._snapped_mouse_world_pos[1])
        self._is_snapped_mouse_over_ui = self._is_screen_position_within_ui(self._snapped_mouse_screen_pos)

        mouse_ui_pos = self._translate_screen_position_to_ui(mouse_screen_pos)

        for icon in self.entity_icons_by_type[self._shown_tab]:
            if icon.contains(mouse_ui_pos):
                self._on_hover_component(icon)
                entity = [e for e in self._entities_by_type[self._shown_tab]
                          if e.map_editor_entity_id == icon.map_editor_entity_id][0]
                self._entity_icon_hovered_by_mouse = entity
                return

        simple_components: List[UiComponent] = self._checkboxes + self._buttons + [self._minimap] \
                                               + self._tab_buttons
        for component in simple_components:
            if component.contains(mouse_ui_pos):
                self._on_hover_component(component)
                return

        if self._is_mouse_button_down and self._is_snapped_mouse_within_world and not self._is_snapped_mouse_over_ui:
            if self._user_state.placing_entity:
                if self._user_state.placing_entity.wall_type or self._user_state.placing_entity.decoration_sprite:
                    return AddEntity(self._snapped_mouse_world_pos, self._user_state.placing_entity)
            elif self._user_state.deleting_entities:
                return DeleteEntities(self._snapped_mouse_world_pos)
            elif self._user_state.deleting_decorations:
                return DeleteDecorations(self._snapped_mouse_world_pos)
            else:
                raise Exception("Unhandled user state: " + str(self._user_state))

        # If something was hovered, we would have returned from the method
        self._set_currently_hovered_component_not_hovered()

    def _on_hover_component(self, component):
        self._set_currently_hovered_component_not_hovered()
        self._hovered_component = component
        self._hovered_component.hovered = True

    def _set_currently_hovered_component_not_hovered(self):
        if self._hovered_component is not None:
            self._hovered_component.hovered = False
            self._hovered_component = None

    def handle_mouse_click(self) -> Optional[MapEditorAction]:

        if self._entity_icon_hovered_by_mouse:
            self._user_state = UserState.placing_entity(self._entity_icon_hovered_by_mouse)

        self._is_mouse_button_down = True
        if self._hovered_component in self._checkboxes:
            self._hovered_component.on_click()
            return None
        if self._hovered_component == self._button_generate_random_map:
            return GenerateRandomMap()
        if self._hovered_component == self._button_save:
            return SaveMap()
        if self._hovered_component == self._minimap:
            mouse_ui_position = self._translate_screen_position_to_ui(self._mouse_screen_pos)
            position_ratio = self._minimap.get_position_ratio(mouse_ui_position)
            return SetCameraPosition(position_ratio)
        for entity_type in self._tab_buttons_by_entity_type:
            if self._hovered_component == self._tab_buttons_by_entity_type[entity_type]:
                self._set_shown_tab(entity_type)

        if self._user_state.placing_entity:
            entity_being_placed = self._user_state.placing_entity
            if self._is_snapped_mouse_within_world and not self._is_snapped_mouse_over_ui:
                return AddEntity(self._snapped_mouse_world_pos, entity_being_placed)

        elif self._user_state.deleting_entities:
            return DeleteEntities(self._snapped_mouse_world_pos)
        else:
            return DeleteDecorations(self._snapped_mouse_world_pos)

    def handle_mouse_release(self):
        self._is_mouse_button_down = False

    def handle_key_down(self, key):
        if key == pygame.K_q:
            self._user_state = UserState.deleting_entities()
        elif key == pygame.K_z:
            self._user_state = UserState.deleting_decorations()
        elif key == pygame.K_v:
            self._set_shown_tab(EntityTab.ITEMS)
        elif key == pygame.K_b:
            self._set_shown_tab(EntityTab.NPCS)
        elif key == pygame.K_n:
            self._set_shown_tab(EntityTab.WALLS)
        elif key == pygame.K_m:
            self._set_shown_tab(EntityTab.MISC)

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self._ui_screen_area.x, position[1] + self._ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self._ui_screen_area.x, position[1] - self._ui_screen_area.y

    def _get_image_for_sprite(self, sprite: Sprite, direction: Direction,
                              animation_progress: float) -> ImageWithRelativePosition:

        images: Dict[Direction, List[ImageWithRelativePosition]] = self._images_by_sprite[sprite]
        if direction in images:
            images_for_this_direction = images[direction]
        else:
            images_for_this_direction = next(iter(images.values()))

        animation_frame_index = int(len(images_for_this_direction) * animation_progress)
        return images_for_this_direction[animation_frame_index]

    def _set_shown_tab(self, shown_tab: EntityTab):
        if self._shown_tab:
            self._tab_buttons_by_entity_type[self._shown_tab].enabled = False
        self._shown_tab = shown_tab
        self._tab_buttons_by_entity_type[shown_tab].enabled = True

    def render(
            self,
            num_enemies: int,
            num_walls: int,
            num_decorations: int,
            npc_positions: List[Tuple[int, int]],
            wall_positions: List[Tuple[int, int]],
            player_position: Tuple[int, int]):

        self._screen_render.rect(COLOR_BLACK, Rect(0, 0, self._camera_size[0], self._camera_size[1]), 3)
        self._screen_render.rect_filled(COLOR_BLACK, Rect(0, self._camera_size[1], self._screen_size[0],
                                                          self._screen_size[1] - self._camera_size[1]))

        self.button_delete_entities.render(self._user_state.deleting_entities)
        self.button_delete_decorations.render(self._user_state.deleting_decorations)

        placing_entity = self._user_state.placing_entity

        for icon in self.entity_icons_by_type[self._shown_tab]:
            highlighted = placing_entity and placing_entity.map_editor_entity_id == icon.map_editor_entity_id
            icon.render(highlighted)

        self._screen_render.rect(COLOR_WHITE, self._ui_screen_area, 1)

        self._screen_render.rect_transparent(Rect(0, 0, 150, 80), 100, COLOR_BLACK)
        self._screen_render.text(self._font_debug_info, "# enemies: " + str(num_enemies), (5, 3))
        self._screen_render.text(self._font_debug_info, "# walls: " + str(num_walls), (5, 20))
        self._screen_render.text(self._font_debug_info, "# decorations: " + str(num_decorations), (5, 37))
        self._screen_render.text(self._font_debug_info, "Cell size: " + str(self.grid_cell_size), (5, 54))

        self._minimap.set_walls(wall_positions)
        self._minimap.update_camera_area(self.camera_world_area)
        self._minimap.update_npc_positions(npc_positions)
        self._minimap.update_player_position(player_position)
        self._minimap.update_world_area(self.world_area)

        for component in self._checkboxes + self._tab_buttons + self._buttons + [self._minimap]:
            component.render()

        if self._hovered_component and self._hovered_component.tooltip:
            tooltip: TooltipGraphics = self._hovered_component.tooltip
            tooltip.render()

        if not self._is_snapped_mouse_over_ui:
            snapped_mouse_rect = Rect(self._snapped_mouse_screen_pos[0], self._snapped_mouse_screen_pos[1],
                                      self.grid_cell_size, self.grid_cell_size)
            if not self._is_snapped_mouse_within_world:
                self._render_map_editor_mouse_rect((250, 50, 0), snapped_mouse_rect)
            elif placing_entity:
                entity_being_placed = placing_entity
                self._render_map_editor_world_entity_at_position(
                    entity_being_placed.sprite, entity_being_placed.entity_size, self._snapped_mouse_screen_pos)
            elif self._user_state.deleting_entities:
                self._render_map_editor_mouse_rect((250, 250, 0), snapped_mouse_rect)
            elif self._user_state.deleting_decorations:
                self._render_map_editor_mouse_rect((0, 250, 250), snapped_mouse_rect)
            else:
                raise Exception("Unhandled user_state: " + str(self._user_state))

    def _render_map_editor_mouse_rect(self, color: Tuple[int, int, int], map_editor_mouse_rect: Rect):
        self._screen_render.rect(color, map_editor_mouse_rect, 3)

    def _render_map_editor_world_entity_at_position(self, sprite: Sprite, entity_size: Tuple[int, int],
                                                    position: Tuple[int, int]):
        image_with_relative_position = self._get_image_for_sprite(sprite, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self._screen_render.image(image_with_relative_position.image, sprite_position)
        self._screen_render.rect((50, 250, 0), Rect(position[0], position[1], entity_size[0], entity_size[1]), 3)

    def _create_map_editor_icon(self, rect: Rect, user_input_key: str,
                                sprite: Optional[Sprite], ui_icon_sprite: Optional[UiIconSprite],
                                map_editor_entity_id: int, tooltip: Optional[TooltipGraphics]) -> MapEditorIcon:
        if sprite:
            image = self._images_by_sprite[sprite][Direction.DOWN][0].image
        elif ui_icon_sprite:
            image = self._images_by_ui_sprite[ui_icon_sprite]
        else:
            raise Exception("Nothing to render!")

        return MapEditorIcon(self._ui_render, rect, image, self._font_ui_icon_keys, user_input_key,
                             map_editor_entity_id, tooltip)

    def _is_screen_position_within_ui(self, screen_position: Tuple[int, int]):
        ui_position = self._translate_screen_position_to_ui(screen_position)
        return ui_position[1] >= 0
