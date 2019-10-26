from typing import Dict, List, Tuple, Optional, Union

import pygame
from pygame.rect import Rect

from pythongame.core.common import Direction, Sprite, ConsumableType, ItemType, HeroId, UiIconSprite
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, ABILITIES, BUFF_TEXTS, \
    KEYS_BY_ABILITY_TYPE, CONSUMABLES, ITEMS, PORTRAIT_ICON_SPRITE_PATHS, \
    HEROES, ConsumableCategory, CHANNELING_BUFFS
from pythongame.core.game_state import WorldEntity, DecorationEntity, NonPlayerCharacter, BuffWithDuration, \
    PlayerState
from pythongame.core.item_inventory import ItemInventorySlot, ItemEquipmentCategory
from pythongame.core.math import is_point_in_rect, sum_of_vectors
from pythongame.core.npc_behaviors import DialogGraphics
from pythongame.core.talents import TalentsGraphics
from pythongame.core.view.image_loading import SpriteInitializer, ImageWithRelativePosition, \
    load_and_scale_sprite, load_and_scale_directional_sprites
from pythongame.core.view.render_util import DrawableArea
from pythongame.core.view.view_state import ViewState, UiToggle
from pythongame.core.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText, VisualSprite, VisualCross
from pythongame.map_editor_world_entity import MapEditorWorldEntity

COLOR_BACKGROUND = (88 + 30, 72 + 30, 40 + 30)
COLOR_BACKGROUND_LINES = (93 + 30, 77 + 30, 45 + 30)

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
COLOR_BORDER = (139, 69, 19)
UI_ICON_SIZE = (32, 32)
PORTRAIT_ICON_SIZE = (100, 70)
MAP_EDITOR_UI_ICON_SIZE = (32, 32)

RENDER_WORLD_COORDINATES = False

DIR_FONTS = './resources/fonts/'


class MouseHoverEvent:
    def __init__(self, item_slot_number: Optional[int], consumable_slot_number: Optional[int],
                 game_world_position: Optional[Tuple[int, int]], ui_toggle: Optional[UiToggle],
                 talent_choice_option: Optional[Tuple[int, int]]):
        self.item_slot_number = item_slot_number
        self.consumable_slot_number = consumable_slot_number
        self.game_world_position = game_world_position
        self.ui_toggle = ui_toggle
        self.talent_choice_option = talent_choice_option  # (choice_index, option_index)


# Used to display some text above an NPC like "[Space] talk"
class EntityActionText:
    def __init__(self, entity: WorldEntity, text: str, details: List[str]):
        self.entity: WorldEntity = entity
        self.text: str = text
        self.details: List[str] = details


class TooltipGraphics:
    def __init__(self, title: str, details: List[str], bottom_left: Optional[Tuple[int, int]] = None,
                 bottom_right: Optional[Tuple[int, int]] = None):
        self.title = title
        self.details = details
        self.bottom_left_corner: Optional[Tuple[int, int]] = bottom_left
        self.bottom_right_corner: Optional[Tuple[int, int]] = bottom_right


class View:

    def __init__(self, camera_size, screen_size):
        pygame.font.init()
        pygame_screen = pygame.display.set_mode(screen_size)
        self.screen_render = DrawableArea(pygame_screen)
        self.ui_render = DrawableArea(pygame_screen, self._translate_ui_position_to_screen)

        self.ui_screen_area = Rect(0, camera_size[1], screen_size[0], screen_size[1] - camera_size[1])
        self.camera_size = camera_size
        self.screen_size = screen_size

        self.font_splash_screen = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 64)

        self.font_ui_stat_bar_numbers = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_money = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_npc_action = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_headers = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 18)
        self.font_tooltip_header = pygame.font.Font(DIR_FONTS + 'Herculanum.ttf', 16)
        self.font_tooltip_details = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_stats = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 9)
        self.font_buff_texts = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_message = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 14)
        self.font_debug_info = pygame.font.Font(None, 19)
        self.font_game_world_text = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 12)
        self.font_game_world_text = pygame.font.Font(None, 19)
        self.font_ui_icon_keys = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 12)
        self.font_level = pygame.font.Font(DIR_FONTS + 'Courier New Bold.ttf', 11)
        self.font_dialog = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 24)
        self.font_dialog_option_detail_body = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)

        self.images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]] = {
            sprite: load_and_scale_directional_sprites(ENTITY_SPRITE_INITIALIZERS[sprite])
            for sprite in ENTITY_SPRITE_INITIALIZERS
        }
        self.images_by_ui_sprite = {sprite: load_and_scale_sprite(
            SpriteInitializer(UI_ICON_SPRITE_PATHS[sprite], UI_ICON_SIZE))
            for sprite in UI_ICON_SPRITE_PATHS
        }
        self.images_by_portrait_sprite = {sprite: load_and_scale_sprite(
            SpriteInitializer(PORTRAIT_ICON_SPRITE_PATHS[sprite], PORTRAIT_ICON_SIZE))
            for sprite in PORTRAIT_ICON_SPRITE_PATHS
        }

        # This is updated every time the view is called
        self.camera_world_area = None

    # ------------------------------------
    #         TRANSLATING COORDINATES
    # ------------------------------------

    def _translate_world_position_to_screen(self, world_position):
        return (self._translate_world_x_to_screen(world_position[0]),
                self._translate_world_y_to_screen(world_position[1]))

    def _translate_screen_position_to_world(self, screen_position):
        return int(screen_position[0] + self.camera_world_area.x), int(screen_position[1] + self.camera_world_area.y)

    def _translate_world_x_to_screen(self, world_x):
        return int(world_x - self.camera_world_area.x)

    def _translate_world_y_to_screen(self, world_y):
        return int(world_y - self.camera_world_area.y)

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_ui_x_to_screen(self, ui_x):
        return ui_x + self.ui_screen_area.x

    def _translate_ui_y_to_screen(self, ui_y):
        return ui_y + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    # ------------------------------------
    #       DRAWING THE GAME WORLD
    # ------------------------------------

    def _world_ground(self, entire_world_area: Rect):
        grid_width = 35
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        column_screen_y_0 = self._translate_world_y_to_screen(self.camera_world_area.y)
        column_screen_y_1 = self._translate_world_y_to_screen(
            min(entire_world_area.y + entire_world_area.h, self.camera_world_area.y + self.camera_world_area.h))
        for i_col in range(num_squares):
            world_x = entire_world_area.x + i_col * grid_width
            if entire_world_area.x < world_x < entire_world_area.x + entire_world_area.w:
                screen_x = self._translate_world_x_to_screen(world_x)
                self.screen_render.line(COLOR_BACKGROUND_LINES, (screen_x, column_screen_y_0),
                                        (screen_x, column_screen_y_1),
                                        1)
        row_screen_x_0 = self._translate_world_x_to_screen(self.camera_world_area.x)
        row_screen_x_1 = self._translate_world_x_to_screen(
            min(entire_world_area.x + entire_world_area.w, self.camera_world_area.x + self.camera_world_area.w))
        for i_row in range(num_squares):
            world_y = entire_world_area.y + i_row * grid_width
            if entire_world_area.y < world_y < entire_world_area.y + entire_world_area.h:
                screen_y = self._translate_world_y_to_screen(world_y)
                self.screen_render.line(COLOR_BACKGROUND_LINES, (row_screen_x_0, screen_y), (row_screen_x_1, screen_y),
                                        1)

        if RENDER_WORLD_COORDINATES:
            for i_col in range(num_squares):
                for i_row in range(num_squares):
                    if i_col % 4 == 0 and i_row % 4 == 0:
                        world_x = entire_world_area.x + i_col * grid_width
                        screen_x = self._translate_world_x_to_screen(world_x)
                        world_y = entire_world_area.y + i_row * grid_width
                        screen_y = self._translate_world_y_to_screen(world_y)
                        self.screen_render.text(self.font_debug_info, str(world_x) + "," + str(world_y),
                                                (screen_x, screen_y),
                                                (250, 250, 250))

    def _world_rect(self, color, world_rect, line_width=0):
        translated_pos = self._translate_world_position_to_screen((world_rect[0], world_rect[1]))
        self.screen_render.rect(color, Rect(translated_pos[0], translated_pos[1], world_rect[2], world_rect[3]),
                                line_width)

    def _world_line(self, color: Tuple[int, int, int], start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                    line_width: int):
        start_position = self._translate_world_position_to_screen(start_pos)
        end_position = self._translate_world_position_to_screen(end_pos)
        self.screen_render.line(color, start_position, end_position, line_width)

    def _world_entity(self, entity: Union[WorldEntity, DecorationEntity]):
        if not entity.visible:
            return
        if entity.sprite is None:
            raise Exception("Entity has no sprite: " + str(entity))
        elif entity.sprite in self.images_by_sprite:
            images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[entity.sprite]
            image_with_relative_position = self._get_image_from_direction(images, entity.direction,
                                                                          entity.movement_animation_progress)
            pos = self._translate_world_position_to_screen((entity.x, entity.y))
            pos = sum_of_vectors(pos, image_with_relative_position.position_relative_to_entity)
            self.screen_render.image(image_with_relative_position.image, pos)
        else:
            raise Exception("Unhandled sprite: " + str(entity.sprite))

    @staticmethod
    def _get_image_from_direction(images: Dict[Direction, List[ImageWithRelativePosition]], direction: Direction,
                                  animation_progress: float) -> ImageWithRelativePosition:
        if direction in images:
            images_for_this_direction = images[direction]
        else:
            images_for_this_direction = next(iter(images.values()))

        animation_frame_index = int(len(images_for_this_direction) * animation_progress)
        return images_for_this_direction[animation_frame_index]

    def _visual_effect(self, visual_effect):
        if isinstance(visual_effect, VisualLine):
            self._visual_line(visual_effect)
        elif isinstance(visual_effect, VisualCircle):
            self._visual_circle(visual_effect)
        elif isinstance(visual_effect, VisualRect):
            self._visual_rect(visual_effect)
        elif isinstance(visual_effect, VisualCross):
            self._visual_cross(visual_effect)
        elif isinstance(visual_effect, VisualText):
            self._visual_text(visual_effect)
        elif isinstance(visual_effect, VisualSprite):
            self._visual_sprite(visual_effect)
        else:
            raise Exception("Unhandled visual effect: " + str(visual_effect))

    def _visual_line(self, line: VisualLine):
        self._world_line(line.color, line.start_position, line.end_position, line.line_width)

    def _visual_circle(self, visual_circle: VisualCircle):
        position = visual_circle.circle()[0]
        radius = visual_circle.circle()[1]
        translated_position = self._translate_world_position_to_screen(position)
        self.screen_render.circle(visual_circle.color, translated_position, radius, visual_circle.line_width)

    def _visual_rect(self, visual_rect: VisualRect):
        self._world_rect(visual_rect.color, visual_rect.rect(), visual_rect.line_width)

    def _visual_cross(self, visual_cross: VisualCross):
        for start_pos, end_pos in visual_cross.lines():
            self._world_line(visual_cross.color, start_pos, end_pos, visual_cross.line_width)

    def _visual_text(self, visual_text: VisualText):
        position = visual_text.position()
        translated_position = self._translate_world_position_to_screen(position)
        self.screen_render.text(self.font_game_world_text, visual_text.text, translated_position, visual_text.color)

    def _visual_sprite(self, visual_sprite: VisualSprite):
        position = visual_sprite.position
        animation_progress = visual_sprite.animation_progress()
        sprite = visual_sprite.sprite
        translated_position = self._translate_world_position_to_screen(position)
        if sprite in self.images_by_sprite:
            images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[sprite]
            image_with_relative_position = self._get_image_from_direction(images, Direction.DOWN,
                                                                          animation_progress)
            pos = sum_of_vectors(translated_position, image_with_relative_position.position_relative_to_entity)
            self.screen_render.image(image_with_relative_position.image, pos)
        else:
            raise Exception("Unhandled sprite: " + str(sprite))

    def _stat_bar_for_world_entity(self, world_entity, h, relative_y, ratio, color):
        position_on_screen = self._translate_world_position_to_screen((world_entity.x, world_entity.y))
        self.screen_render.stat_bar(position_on_screen[0] + 1, position_on_screen[1] + relative_y,
                                    world_entity.w - 2, h, ratio, color, False)

    # ------------------------------------
    #           DRAWING THE UI
    # ------------------------------------

    def _stat_bar_in_ui(self, position_in_ui, w, h, ratio_filled: float, color, border: bool):
        x, y = self._translate_ui_position_to_screen(position_in_ui)
        self.screen_render.stat_bar(x, y, w, h, ratio_filled, color, border)

    def _consumable_icon_in_ui(self, x_in_ui, y_in_ui, size, consumable_number: int,
                               consumable_types: List[ConsumableType], highlighted_consumable_action: int):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self.screen_render.rect_filled((40, 40, 50), Rect(x, y, w, h))
        if consumable_types:
            icon_sprite = CONSUMABLES[consumable_types[0]].icon_sprite
            self.screen_render.image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self.screen_render.rect((150, 150, 190), Rect(x, y, w, h), 1)
        # Render any consumables that are deeper down in the inventory
        sub_rect_h = 3
        for i in range(len(consumable_types)):
            sub_consumable_type = consumable_types[i]
            consumable_category = CONSUMABLES[sub_consumable_type].category
            if consumable_category == ConsumableCategory.HEALTH:
                sub_rect_color = (160, 110, 110)
            elif consumable_category == ConsumableCategory.MANA:
                sub_rect_color = (110, 110, 200)
            else:
                sub_rect_color = (170, 170, 170)
            self.screen_render.rect_filled(sub_rect_color, Rect(x, y - 2 - (sub_rect_h + 1) * (i + 1), w, sub_rect_h))

        if highlighted_consumable_action == consumable_number:
            self.screen_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        self.screen_render.text(self.font_ui_icon_keys, str(consumable_number), (x + 12, y + h + 4))

    def _ability_icon_in_ui(self, x_in_ui, y_in_ui, size, ability_type, highlighted_ability_action,
                            ability_cooldowns_remaining):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        ability = ABILITIES[ability_type]
        ability_key = KEYS_BY_ABILITY_TYPE[ability_type]
        icon_sprite = ability.icon_sprite
        icon_rect = Rect(x, y, w, h)
        self.screen_render.rect_filled((40, 40, 50), icon_rect)
        self.screen_render.image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self.screen_render.rect((150, 150, 190), icon_rect, 1)
        if highlighted_ability_action == ability_type:
            self.screen_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        self.screen_render.text(self.font_ui_icon_keys, ability_key.key_string, (x + 12, y + h + 4))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / ability.cooldown
            cooldown_rect = Rect(x + 1, y + 1 + (h - 2) * (1 - ratio_remaining), w - 2, (h - 2) * ratio_remaining + 1)
            self.screen_render.rect_filled((100, 30, 30), cooldown_rect)
            self.screen_render.rect((180, 30, 30), icon_rect, 2)

    def _item_icon_in_ui(self, x_in_ui, y_in_ui, size, item_type: ItemType,
                         slot_equipment_category: ItemEquipmentCategory):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        rect = Rect(x, y, w, h)
        self.screen_render.rect_filled((40, 40, 50), rect)
        if item_type:
            if slot_equipment_category:
                self.screen_render.rect_filled((40, 40, 70), rect)
            ui_icon_sprite = ITEMS[item_type].icon_sprite
            self.screen_render.image(self.images_by_ui_sprite[ui_icon_sprite], (x, y))
        elif slot_equipment_category:
            if slot_equipment_category == ItemEquipmentCategory.HEAD:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_HELMET], (x, y))
            elif slot_equipment_category == ItemEquipmentCategory.CHEST:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_CHEST], (x, y))
            elif slot_equipment_category == ItemEquipmentCategory.MAIN_HAND:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_MAINHAND], (x, y))
            elif slot_equipment_category == ItemEquipmentCategory.OFF_HAND:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_OFFHAND], (x, y))
            elif slot_equipment_category == ItemEquipmentCategory.NECK:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_NECK], (x, y))
            elif slot_equipment_category == ItemEquipmentCategory.RING:
                self.screen_render.image(self.images_by_ui_sprite[UiIconSprite.INVENTORY_TEMPLATE_RING], (x, y))
        if item_type and slot_equipment_category:
            color_outline = (250, 250, 250)
        else:
            color_outline = (100, 100, 140)
        self.screen_render.rect(color_outline, rect, 1)

    def _map_editor_icon_in_ui(self, x_in_ui, y_in_ui, size: Tuple[int, int], highlighted: bool, user_input_key: str,
                               sprite: Optional[Sprite], ui_icon_sprite: Optional[UiIconSprite]):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))

        self.screen_render.rect_filled((40, 40, 40), Rect(x, y, w, h))

        if sprite:
            image = self.images_by_sprite[sprite][Direction.DOWN][0].image
        elif ui_icon_sprite:
            image = self.images_by_ui_sprite[ui_icon_sprite]
        else:
            raise Exception("Nothing to render!")

        icon_scaled_image = pygame.transform.scale(image, size)
        self.screen_render.image(icon_scaled_image, (x, y))

        self.screen_render.rect(COLOR_WHITE, Rect(x, y, w, h), 2)
        if highlighted:
            self.screen_render.rect(COLOR_HIGHLIGHTED_ICON, Rect(x - 1, y - 1, w + 2, h + 2), 3)
        self.screen_render.text(self.font_ui_icon_keys, user_input_key, (x + 12, y + h + 4))

    def _minimap_in_ui(self, position_in_ui, size, player_relative_position):
        pos_in_screen = self._translate_ui_position_to_screen(position_in_ui)
        rect_in_screen = Rect(pos_in_screen[0], pos_in_screen[1], size[0], size[1])
        self.screen_render.rect_filled((40, 40, 50), rect_in_screen)
        self.screen_render.rect((150, 150, 190), rect_in_screen, 1)
        dot_x = rect_in_screen[0] + player_relative_position[0] * size[0]
        dot_y = rect_in_screen[1] + player_relative_position[1] * size[1]
        dot_w = 4
        self.screen_render.rect_filled((100, 160, 100), Rect(dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))

    def _message(self, message):
        w_rect = len(message) * 9 + 10
        x_message = self.ui_screen_area.w / 2 - w_rect / 2
        y_message = self.ui_screen_area.y - 30
        self.screen_render.rect_transparent(Rect(x_message - 10, y_message - 5, w_rect, 28), 135, (0, 0, 0))
        self.screen_render.text(self.font_message, message, (x_message, y_message))

    def _tooltip(self, tooltip: TooltipGraphics):

        detail_lines = []
        detail_max_line_length = 32
        for detail in tooltip.details:
            detail_lines += self._split_text_into_lines(detail, detail_max_line_length)

        w_tooltip = 260
        h_tooltip = 60 + 17 * len(detail_lines)
        if tooltip.bottom_left_corner is not None:
            bottom_left_corner = tooltip.bottom_left_corner
        else:
            bottom_left_corner = (tooltip.bottom_right_corner[0] - w_tooltip, tooltip.bottom_right_corner[1])
        x_tooltip = bottom_left_corner[0]
        y_tooltip = bottom_left_corner[1] - h_tooltip - 3
        rect_tooltip = Rect(x_tooltip, y_tooltip, w_tooltip, h_tooltip)
        self.screen_render.rect_transparent(Rect(x_tooltip, y_tooltip, w_tooltip, h_tooltip), 200, (0, 0, 30))
        self.screen_render.rect(COLOR_WHITE, rect_tooltip, 1)
        self.screen_render.text(self.font_tooltip_header, tooltip.title, (x_tooltip + 20, y_tooltip + 15), COLOR_WHITE)
        y_separator = y_tooltip + 40
        self.screen_render.line(COLOR_WHITE, (x_tooltip + 10, y_separator), (x_tooltip + w_tooltip - 10, y_separator),
                                1)

        for i, line in enumerate(detail_lines):
            self.screen_render.text(self.font_tooltip_details, line, (x_tooltip + 20, y_tooltip + 50 + i * 18),
                                    COLOR_WHITE)

    def _entity_action_text(self, entity_action_text: EntityActionText):
        entity_center_pos = self._translate_world_position_to_screen(entity_action_text.entity.get_center_position())
        text = entity_action_text.text
        detail_lines = []
        for detail_entry in entity_action_text.details:
            detail_lines += self._split_text_into_lines(detail_entry, 30)
        if detail_lines:
            line_length = max(max([len(line) for line in detail_lines]), len(text))
        else:
            line_length = len(text)
        rect_width = line_length * 8
        rect_height = 16 + len(detail_lines) * 16
        rect_pos = (entity_center_pos[0] - rect_width // 2, entity_center_pos[1] - 60)
        self.screen_render.rect_transparent(Rect(rect_pos[0], rect_pos[1], rect_width, rect_height), 150, (0, 0, 0))
        self.screen_render.text(self.font_npc_action, text, (rect_pos[0] + 4, rect_pos[1]))
        for i, detail_line in enumerate(detail_lines):
            self.screen_render.text(self.font_npc_action, detail_line, (rect_pos[0] + 4, rect_pos[1] + (i + 1) * 16))

    def render_world(self, all_entities_to_render: List[WorldEntity], decorations_to_render: List[DecorationEntity],
                     camera_world_area, non_player_characters: List[NonPlayerCharacter], is_player_invisible: bool,
                     player_active_buffs: List[BuffWithDuration],
                     player_entity: WorldEntity, visual_effects, render_hit_and_collision_boxes, player_health,
                     player_max_health, entire_world_area: Rect, entity_action_text: Optional[EntityActionText]):
        self.camera_world_area = camera_world_area

        self.screen_render.fill(COLOR_BACKGROUND)
        self._world_ground(entire_world_area)

        all_entities_to_render.sort(key=lambda entry: (-entry.view_z, entry.y))

        for decoration_entity in decorations_to_render:
            self._world_entity(decoration_entity)

        for entity in all_entities_to_render:
            self._world_entity(entity)
            if entity == player_entity and is_player_invisible:
                self._world_rect((200, 100, 250), player_entity.rect(), 2)

        player_sprite_y_relative_to_entity = \
            ENTITY_SPRITE_INITIALIZERS[player_entity.sprite][Direction.DOWN].position_relative_to_entity[1]
        if player_entity.visible:
            self._stat_bar_for_world_entity(player_entity, 5, player_sprite_y_relative_to_entity - 5,
                                            player_health / player_max_health, (100, 200, 0))

        # Buffs related to channeling something are rendered above player's head with progress from left to right
        for buff in player_active_buffs:
            if buff.buff_effect.get_buff_type() in CHANNELING_BUFFS:
                ratio = 1 - buff.get_ratio_duration_remaining()
                self._stat_bar_for_world_entity(player_entity, 3, player_sprite_y_relative_to_entity - 11, ratio,
                                                (150, 150, 250))

        if render_hit_and_collision_boxes:
            for entity in all_entities_to_render:
                # hit box
                self._world_rect((250, 250, 250), entity.rect(), 1)

        for npc in non_player_characters:
            healthbar_color = COLOR_RED if npc.is_enemy else (250, 250, 0)
            npc_sprite_y_relative_to_entity = \
                ENTITY_SPRITE_INITIALIZERS[npc.world_entity.sprite][Direction.DOWN].position_relative_to_entity[1]
            if not npc.is_neutral:
                self._stat_bar_for_world_entity(npc.world_entity, 3, npc_sprite_y_relative_to_entity - 5,
                                                npc.health_resource.get_partial(), healthbar_color)
            if npc.active_buffs:
                buff = npc.active_buffs[0]
                if buff.should_duration_be_visualized_on_enemies():
                    self._stat_bar_for_world_entity(npc.world_entity, 2, npc_sprite_y_relative_to_entity - 9,
                                                    buff.get_ratio_duration_remaining(), (250, 250, 250))
        for visual_effect in visual_effects:
            self._visual_effect(visual_effect)

        if entity_action_text:
            self._entity_action_text(entity_action_text)

    def render_ui(
            self,
            player_state: PlayerState,
            view_state: ViewState,
            fps_string: str,
            is_paused: bool,
            player_speed_multiplier: float,
            mouse_screen_position: Tuple[int, int],
            dialog: Optional[DialogGraphics],
            talents: TalentsGraphics) -> MouseHoverEvent:

        player_health = player_state.health_resource.value
        player_max_health = player_state.health_resource.max_value
        player_max_mana = player_state.mana_resource.max_value
        player_mana = player_state.mana_resource.value
        player_active_buffs = player_state.active_buffs
        consumable_slots = player_state.consumable_inventory.consumables_in_slots
        ability_cooldowns_remaining = player_state.ability_cooldowns_remaining
        abilities = player_state.abilities
        item_slots: List[ItemInventorySlot] = player_state.item_inventory.slots
        player_exp = player_state.exp
        player_max_exp_in_this_level = player_state.max_exp_in_this_level
        player_level = player_state.level
        player_money = player_state.money
        hero_id = player_state.hero_id

        player_minimap_relative_position = view_state.player_minimap_relative_position
        message = view_state.message
        highlighted_consumable_action = view_state.highlighted_consumable_action
        highlighted_ability_action = view_state.highlighted_ability_action

        hovered_item_slot_number = None
        hovered_consumable_slot_number = None
        hovered_ui_toggle = None
        hovered_talent_option: Optional[Tuple[int, int]] = None
        is_mouse_hovering_ui = is_point_in_rect(mouse_screen_position, self.ui_screen_area)

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)
        tooltip: Optional[TooltipGraphics] = None
        self.screen_render.rect(COLOR_BORDER, Rect(0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self.screen_render.rect_filled((20, 10, 0), Rect(0, self.camera_size[1], self.screen_size[0],
                                                         self.screen_size[1] - self.camera_size[1]))

        y_0 = 5

        y_1 = 30
        y_2 = y_1 + 22
        y_3 = 90
        y_4 = y_3 + 22

        x_1 = 140

        x_exp_bar = x_1
        self.ui_render.text(self.font_level, "Level " + str(player_level), (x_exp_bar, y_0))
        self._stat_bar_in_ui((x_exp_bar, y_0 + 18), 380, 2, player_exp / player_max_exp_in_this_level, (200, 200, 200),
                             True)

        x_0 = 20

        self._player_portrait(hero_id, (x_0, y_0 + 13))

        rect_healthbar = Rect(x_0, y_4 - 1, 100, 14)
        self._stat_bar_in_ui((rect_healthbar[0], rect_healthbar[1]), rect_healthbar[2], rect_healthbar[3],
                             player_health / player_max_health, (200, 0, 50), True)
        if is_point_in_rect(mouse_ui_position, rect_healthbar):
            tooltip_details = [
                "regeneration: " + "{:.1f}".format(player_state.health_resource.get_effective_regen()) + "/s"]
            tooltip_bottom_left_position = self._translate_ui_position_to_screen((rect_healthbar[0], rect_healthbar[1]))
            tooltip = TooltipGraphics("Health", tooltip_details, bottom_left=tooltip_bottom_left_position)
        health_text = str(player_health) + "/" + str(player_max_health)
        self.ui_render.text(self.font_ui_stat_bar_numbers, health_text, (x_0 + 20, y_4 - 1))

        rect_manabar = Rect(x_0, y_4 + 20, 100, 14)
        self._stat_bar_in_ui((rect_manabar[0], rect_manabar[1]), rect_manabar[2], rect_manabar[3],
                             player_mana / player_max_mana, (50, 0, 200), True)
        if is_point_in_rect(mouse_ui_position, rect_manabar):
            tooltip_details = [
                "regeneration: " + "{:.1f}".format(player_state.mana_resource.get_effective_regen()) + "/s"]
            tooltip_bottom_left_position = self._translate_ui_position_to_screen((rect_manabar[0], rect_manabar[1]))
            tooltip = TooltipGraphics("Mana", tooltip_details, bottom_left=tooltip_bottom_left_position)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self.ui_render.text(self.font_ui_stat_bar_numbers, mana_text, (x_0 + 20, y_4 + 20))

        self.ui_render.text(self.font_ui_money, "Money: " + str(player_money), (x_0 + 4, y_4 + 38))

        # CONSUMABLES
        icon_space = 2
        icon_rect_padding = 2
        consumables_rect_pos = self._translate_ui_position_to_screen((x_1 - icon_rect_padding, y_2 - icon_rect_padding))
        consumables_rect = Rect(
            consumables_rect_pos[0], consumables_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * len(consumable_slots) - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self.screen_render.rect_filled((60, 60, 80), consumables_rect)
        for i, slot_number in enumerate(consumable_slots):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            consumable_types = consumable_slots[slot_number]
            consumable_type = consumable_types[0] if consumable_types else None
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                hovered_consumable_slot_number = slot_number
                if consumable_type:
                    tooltip_title = CONSUMABLES[consumable_type].name
                    tooltip_details = [CONSUMABLES[consumable_type].description]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
                    tooltip = TooltipGraphics(tooltip_title, tooltip_details, bottom_left=tooltip_bottom_left_position)
            self._consumable_icon_in_ui(x, y, UI_ICON_SIZE, slot_number, consumable_types,
                                        highlighted_consumable_action)

        # ABILITIES
        abilities_rect_pos = self._translate_ui_position_to_screen((x_1 - icon_rect_padding, y_4 - icon_rect_padding))
        max_num_abilities = 5
        abilities_rect = Rect(
            abilities_rect_pos[0], abilities_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * max_num_abilities - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self.screen_render.rect_filled((60, 60, 80), abilities_rect)
        for i, ability_type in enumerate(abilities):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_4
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                if ability_type:
                    ability_data = ABILITIES[ability_type]
                    tooltip_title = ability_data.name
                    cooldown = str(ability_data.cooldown / 1000.0)
                    mana_cost = str(ability_data.mana_cost)
                    tooltip_details = ["Cooldown: " + cooldown + " s", "Mana: " + mana_cost, ability_data.description]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
                    tooltip = TooltipGraphics(tooltip_title, tooltip_details, bottom_left=tooltip_bottom_left_position)
            self._ability_icon_in_ui(x, y, UI_ICON_SIZE, ability_type,
                                     highlighted_ability_action, ability_cooldowns_remaining)

        # ITEMS
        x_2 = 325
        items_rect_pos = self._translate_ui_position_to_screen((x_2 - icon_rect_padding, y_2 - icon_rect_padding))
        num_item_slot_rows = 3
        num_slots_per_row = 3
        items_rect = Rect(
            items_rect_pos[0], items_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * num_slots_per_row - icon_space + icon_rect_padding * 2,
            num_item_slot_rows * UI_ICON_SIZE[1] + (num_item_slot_rows - 1) * icon_space + icon_rect_padding * 2)
        self.screen_render.rect_filled((60, 60, 80), items_rect)
        for i in range(len(item_slots)):
            x = x_2 + (i % num_slots_per_row) * (UI_ICON_SIZE[0] + icon_space)
            y = y_2 + (i // num_slots_per_row) * (UI_ICON_SIZE[1] + icon_space)
            slot: ItemInventorySlot = item_slots[i]
            item_type = slot.get_item_type() if not slot.is_empty() else None
            slot_equipment_category = slot.enforced_equipment_category
            if is_point_in_rect(mouse_ui_position, Rect(x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                hovered_item_slot_number = i
                if item_type:
                    item_data = ITEMS[item_type]
                    tooltip_title = item_data.name
                    tooltip_details = []
                    if item_data.item_equipment_category:
                        tooltip_details.append("[" + item_data.item_equipment_category.name + "]")
                    tooltip_details += item_data.description_lines
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
                    tooltip = TooltipGraphics(tooltip_title, tooltip_details, bottom_left=tooltip_bottom_left_position)
                elif slot_equipment_category:
                    tooltip_title = "..."  # "[" + slot_equipment_category.name + "]"
                    tooltip_details = ["[" + slot_equipment_category.name + "]",
                                       "You have nothing equipped. Drag an item here to equip it!"]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
                    tooltip = TooltipGraphics(tooltip_title, tooltip_details, bottom_left=tooltip_bottom_left_position)
            self._item_icon_in_ui(x, y, UI_ICON_SIZE, item_type, slot_equipment_category)

        # MINIMAP
        x_3 = 440
        minimap_padding_rect_pos = self._translate_ui_position_to_screen((x_3 - 2, y_2 - 2))
        minimap_padding_rect = Rect(minimap_padding_rect_pos[0], minimap_padding_rect_pos[1], 80 + 4, 80 + 4)
        self.screen_render.rect_filled((60, 60, 80), minimap_padding_rect)
        self._minimap_in_ui((x_3, y_2), (80, 80), player_minimap_relative_position)

        if dialog:
            self._dialog(dialog)

        # BUFFS
        x_buffs = 10
        buff_texts = []
        buff_duration_ratios_remaining = []
        for active_buff in player_active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            # Buffs that don't have description texts shouldn't be displayed. (They are typically irrelevant to the
            # player)
            if buff_type in BUFF_TEXTS:
                buff_texts.append(BUFF_TEXTS[buff_type])
                buff_duration_ratios_remaining.append(active_buff.get_ratio_duration_remaining())
        num_buffs_to_render = len(buff_texts)
        y_buffs = -35 - (num_buffs_to_render - 1) * 25
        buffs_screen_position = self._translate_ui_position_to_screen((x_buffs, y_buffs))
        if num_buffs_to_render:
            rect_padding = 5
            # Note: The width of this rect is hard-coded so long buff descriptions aren't well supported
            buffs_background_rect = Rect(
                buffs_screen_position[0] - rect_padding,
                buffs_screen_position[1] - rect_padding,
                140 + rect_padding * 2,
                num_buffs_to_render * 25 + rect_padding * 2)
            self.screen_render.rect_transparent(buffs_background_rect, 125, COLOR_BLACK)
        for i, text in enumerate(buff_texts):
            y_offset_buff = i * 25
            y = y_buffs + y_offset_buff
            self.ui_render.text(self.font_buff_texts, text, (x_buffs, y))
            self._stat_bar_in_ui((x_buffs, y + 20), 60, 2, buff_duration_ratios_remaining[i],
                                 (250, 250, 0), False)

        # TOGGLES
        pos_toggled_content = (545, -300)
        x_toggles = 555
        if view_state.toggle_enabled == UiToggle.STATS:
            self._render_stats(player_speed_multiplier, player_state, pos_toggled_content)
        elif view_state.toggle_enabled == UiToggle.TALENTS:
            hovered_talent_option, talent_tooltip = self._render_talents(
                talents, pos_toggled_content, mouse_ui_position)
            tooltip = talent_tooltip if talent_tooltip is not None else tooltip
        is_mouse_hovering_stats_toggle = self._toggle_in_ui(
            x_toggles, y_1, "STATS", view_state.toggle_enabled == UiToggle.STATS, mouse_ui_position)
        is_mouse_hovering_talents_toggle = self._toggle_in_ui(
            x_toggles, y_1 + 30, "TALENTS", view_state.toggle_enabled == UiToggle.TALENTS,
            mouse_ui_position)
        if is_mouse_hovering_stats_toggle:
            hovered_ui_toggle = UiToggle.STATS
        elif is_mouse_hovering_talents_toggle:
            hovered_ui_toggle = UiToggle.TALENTS

        self.screen_render.rect(COLOR_BORDER, self.ui_screen_area, 1)

        self.screen_render.rect_transparent(Rect(0, 0, 50, 20), 100, COLOR_BLACK)
        self.screen_render.text(self.font_debug_info, fps_string + " fps", (5, 3))

        if message:
            self._message(message)

        if tooltip:
            self._tooltip(tooltip)

        if is_paused:
            self.screen_render.rect_transparent(Rect(0, 0, self.screen_size[0], self.screen_size[1]), 140, COLOR_BLACK)
            self._splash_screen_text("PAUSED", self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50)

        mouse_game_world_position = None
        if not is_mouse_hovering_ui:
            mouse_game_world_position = self._translate_screen_position_to_world(mouse_screen_position)
        return MouseHoverEvent(hovered_item_slot_number, hovered_consumable_slot_number, mouse_game_world_position,
                               hovered_ui_toggle, hovered_talent_option)

    def _toggle_in_ui(self, x: int, y: int, text: str, enabled: bool, mouse_ui_position: Tuple[int, int]) -> bool:
        rect = Rect(x, y, 120, 20)
        if enabled:
            self.ui_render.rect_filled((50, 50, 150), rect)
        self.ui_render.rect(COLOR_WHITE, rect, 1)
        self.ui_render.text(self.font_tooltip_details, text, (x + 20, y + 2))
        return is_point_in_rect(mouse_ui_position, rect)

    def _render_stats(self, player_speed_multiplier: float, player_state: PlayerState, ui_position: Tuple[int, int]):

        rect_container = Rect(ui_position[0], ui_position[1], 140, 170)
        self.ui_render.rect_transparent(rect_container, 140, (0, 0, 30))

        self.ui_render.text(self.font_tooltip_details, "STATS:", (ui_position[0] + 45, ui_position[1] + 10))

        player_life_steal = player_state.life_steal_ratio
        health_regen_text = \
            "  health reg: " + "{:.1f}".format(player_state.health_resource.base_regen)
        if player_state.health_resource.regen_bonus > 0:
            health_regen_text += " +" + "{:.1f}".format(player_state.health_resource.regen_bonus)
        mana_regen_text = \
            "    mana reg: " + "{:.1f}".format(player_state.mana_resource.base_regen)
        if player_state.mana_resource.regen_bonus > 0:
            mana_regen_text += " +" + "{:.1f}".format(player_state.mana_resource.regen_bonus)
        damage_stat_text = \
            "    % damage: " + str(int(round(player_state.base_damage_modifier * 100)))
        if player_state.damage_modifier_bonus > 0:
            damage_stat_text += " +" + str(int(round(player_state.damage_modifier_bonus * 100)))
        speed_stat_text = \
            "     % speed: " + ("+" if player_speed_multiplier >= 1 else "") \
            + str(int(round((player_speed_multiplier - 1) * 100)))
        lifesteal_stat_text = \
            "% life steal: " + str(int(round(player_life_steal * 100)))
        armor_stat_text = \
            "       armor: " + str(player_state.base_armor)
        if player_state.armor_bonus > 0:
            armor_stat_text += " +" + str(player_state.armor_bonus)
        elif player_state.armor_bonus < 0:
            armor_stat_text += " " + str(player_state.armor_bonus)
        x_text = ui_position[0] + 7
        y_0 = ui_position[1] + 45
        self.ui_render.text(self.font_stats, health_regen_text, (x_text, y_0), COLOR_WHITE)
        self.ui_render.text(self.font_stats, mana_regen_text, (x_text, y_0 + 20), COLOR_WHITE)
        self.ui_render.text(self.font_stats, damage_stat_text, (x_text, y_0 + 40), COLOR_WHITE)
        self.ui_render.text(self.font_stats, speed_stat_text, (x_text, y_0 + 60), COLOR_WHITE)
        self.ui_render.text(self.font_stats, lifesteal_stat_text, (x_text, y_0 + 80), COLOR_WHITE)
        self.ui_render.text(self.font_stats, armor_stat_text, (x_text, y_0 + 100), COLOR_WHITE)

    def _render_talents(self, talents: TalentsGraphics, ui_position: Tuple[int, int],
                        mouse_ui_position: Tuple[int, int]) -> Tuple[
        Optional[Tuple[int, int]], Optional[TooltipGraphics]]:

        tooltip_graphics: TooltipGraphics = None
        hovered_talent_option = None

        rect_container = Rect(ui_position[0], ui_position[1], 140, 260)
        self.ui_render.rect_transparent(rect_container, 140, (0, 0, 30))

        self.ui_render.text(self.font_tooltip_details, "TALENTS:", (ui_position[0] + 35, ui_position[1] + 10))

        x_text = ui_position[0] + 22
        y_0 = ui_position[1] + 35
        for i, choice_graphics in enumerate(talents.choice_graphics_items):
            y = y_0 + i * (UI_ICON_SIZE[1] + 30)
            y_icon = y + 3
            choice = choice_graphics.choice
            self.ui_render.text(self.font_stats, choice.first.name, (x_text, y_icon + UI_ICON_SIZE[1] + 5), COLOR_WHITE)
            self.ui_render.text(self.font_stats, choice.second.name, (x_text + 60, y_icon + UI_ICON_SIZE[1] + 5),
                                COLOR_WHITE)
            is_mouse_hovering_first = self._render_talent_icon(
                choice.first.ui_icon_sprite, (x_text, y_icon), choice_graphics.chosen_index == 0, mouse_ui_position)
            is_mouse_hovering_second = self._render_talent_icon(
                choice.second.ui_icon_sprite, (x_text + 60, y_icon), choice_graphics.chosen_index == 1,
                mouse_ui_position)

            if is_mouse_hovering_first:
                hovered_talent_option = (i, 0)
                tooltip_graphics = TooltipGraphics(
                    choice.first.name, [choice.first.description],
                    bottom_right=self._translate_ui_position_to_screen((x_text + UI_ICON_SIZE[0], y_icon)))
            elif is_mouse_hovering_second:
                hovered_talent_option = (i, 1)
                tooltip_graphics = TooltipGraphics(
                    choice.second.name, [choice.second.description],
                    bottom_right=self._translate_ui_position_to_screen((x_text + UI_ICON_SIZE[0] + 60, y_icon)))

        y_bot_text = rect_container[1] + rect_container[3] - 26

        if talents.choice_graphics_items:
            player_can_choose = talents.choice_graphics_items[-1].chosen_index is None
            if player_can_choose:
                self.ui_render.text(self.font_stats, "Choose a talent!", (x_text, y_bot_text))
        else:
            self.ui_render.text(self.font_stats, "No talents yet!", (x_text, y_bot_text))

        return hovered_talent_option, tooltip_graphics

    def _render_talent_icon(self, ui_icon_sprite: UiIconSprite, position: Tuple[int, int], chosen: bool,
                            mouse_ui_position: Tuple[int, int]) -> bool:
        translated_pos = self._translate_ui_position_to_screen(position)
        rect = Rect(translated_pos[0], translated_pos[1], UI_ICON_SIZE[0], UI_ICON_SIZE[1])
        self.screen_render.rect_filled(COLOR_BLACK, rect)
        image = self.images_by_ui_sprite[ui_icon_sprite]
        self.screen_render.image(image, translated_pos)
        color_outline = COLOR_HIGHLIGHTED_ICON if chosen else COLOR_WHITE
        width_outline = 2 if chosen else 1
        self.screen_render.rect(color_outline, rect, width_outline)
        return is_point_in_rect(mouse_ui_position, Rect(position[0], position[1], UI_ICON_SIZE[0], UI_ICON_SIZE[1]))

    def _player_portrait(self, hero_id: HeroId, ui_position: Tuple[int, int]):
        rect_portrait_pos = self._translate_ui_position_to_screen(ui_position)
        portrait_sprite = HEROES[hero_id].portrait_icon_sprite
        player_portrait_image = self.images_by_portrait_sprite[portrait_sprite]
        self.screen_render.image(player_portrait_image, rect_portrait_pos)
        self.screen_render.rect((160, 160, 180),
                                Rect(rect_portrait_pos[0], rect_portrait_pos[1], PORTRAIT_ICON_SIZE[0],
                                     PORTRAIT_ICON_SIZE[1]),
                                2)

    def _dialog(self, dialog_graphics: DialogGraphics):

        tall_detail_section = any(
            [o.detail_body is not None or o.detail_header is not None or o.detail_ui_icon_sprite is not None
             for o in dialog_graphics.options])

        h_detail_section_expansion = 82

        options_margin = 10
        option_padding = 4
        h_option_line = 20
        if tall_detail_section:
            h_dialog_container = 310 + len(dialog_graphics.options) * (h_option_line + 2 * option_padding)
        else:
            h_dialog_container = 310 + len(dialog_graphics.options) * (h_option_line + 2 * option_padding) \
                                 - h_detail_section_expansion
        rect_dialog_container = Rect(100, 35, 500, h_dialog_container)

        x_left = rect_dialog_container[0]
        x_right = rect_dialog_container[0] + rect_dialog_container[2]
        self.screen_render.rect((210, 180, 60), rect_dialog_container, 5)
        self.screen_render.rect_transparent(rect_dialog_container, 200, COLOR_BLACK)
        color_separator = (170, 140, 20)
        dialog_container_portrait_padding = 10
        rect_portrait_pos = (x_left + dialog_container_portrait_padding,
                             rect_dialog_container[1] + dialog_container_portrait_padding)
        dialog_image = self.images_by_portrait_sprite[dialog_graphics.portrait_icon_sprite]
        self.screen_render.image(dialog_image, rect_portrait_pos)
        rect_portrait = Rect(rect_portrait_pos[0], rect_portrait_pos[1], PORTRAIT_ICON_SIZE[0], PORTRAIT_ICON_SIZE[1])
        self.screen_render.rect((160, 160, 180), rect_portrait, 2)

        dialog_pos = (x_left + 120, rect_dialog_container[1] + 15)
        dialog_lines = self._split_text_into_lines(dialog_graphics.text_body, 35)
        for i, dialog_text_line in enumerate(dialog_lines):
            if i == 6:
                print("WARN: too long dialog for NPC!")
                break
            self.screen_render.text(self.font_dialog, dialog_text_line, (dialog_pos[0] + 5, dialog_pos[1] + 32 * i),
                                    COLOR_WHITE)

        y_above_options = dialog_pos[1] + 150
        self.screen_render.line(color_separator, (x_left, y_above_options), (x_right, y_above_options), 2)

        for i, option in enumerate(dialog_graphics.options):
            x_option = x_left + 8
            y_option = y_above_options + options_margin + i * (h_option_line + 2 * option_padding)
            x_option_text = x_option + option_padding + 5
            y_option_text = y_option + option_padding + 2
            color_highlight = COLOR_WHITE

            is_option_active = dialog_graphics.active_option_index == i
            color_option_text = COLOR_WHITE if is_option_active else (160, 160, 160)
            if is_option_active:
                rect_highlight_active_option = Rect(
                    x_option, y_option, rect_dialog_container[2] - 16, h_option_line + 2 * option_padding)
                self.screen_render.rect_transparent(rect_highlight_active_option, 120, COLOR_WHITE)
                self.screen_render.rect(color_highlight, rect_highlight_active_option, 1)
            self.screen_render.text(self.font_dialog, option.summary, (x_option_text, y_option_text), color_option_text)

        active_option = dialog_graphics.options[dialog_graphics.active_option_index]
        y_under_options = y_above_options + 2 * options_margin \
                          + len(dialog_graphics.options) * (h_option_line + 2 * option_padding)
        self.screen_render.line(color_separator, (x_left, y_under_options), (x_right, y_under_options), 2)

        if tall_detail_section:
            y_action_text = y_under_options + 15 + h_detail_section_expansion
        else:
            y_action_text = y_under_options + 15

        if tall_detail_section:
            if active_option.detail_ui_icon_sprite is not None:
                active_option_image = self.images_by_ui_sprite[active_option.detail_ui_icon_sprite]
                pos_option_image = x_left + 6, y_under_options + 7
                self.screen_render.image(active_option_image, pos_option_image)
                rect_option_image = Rect(pos_option_image[0], pos_option_image[1], UI_ICON_SIZE[0], UI_ICON_SIZE[1])
                self.screen_render.rect((150, 150, 150), rect_option_image, 1)
            if active_option.detail_header is not None:
                self.screen_render.text(self.font_dialog, active_option.detail_header,
                                        (x_left + 14 + UI_ICON_SIZE[0] + 4, y_action_text - h_detail_section_expansion))
            if active_option.detail_body is not None:
                detail_body_lines = self._split_text_into_lines(active_option.detail_body, 70)
                for i, line in enumerate(detail_body_lines):
                    line_pos = (x_left + 10, y_action_text - h_detail_section_expansion + 35 + 20 * i)
                    self.screen_render.text(self.font_dialog_option_detail_body, line, line_pos)
        action_text = active_option.detail_action_text
        self.screen_render.text(self.font_dialog, "[Space] : " + action_text, (x_left + 10, y_action_text))

    @staticmethod
    def _split_text_into_lines(full_text: str, max_line_length: int) -> List[str]:
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

    def render_item_being_dragged(self, item_type: ItemType, mouse_screen_position: Tuple[int, int]):
        ui_icon_sprite = ITEMS[item_type].icon_sprite
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] // 2, mouse_screen_position[1] - UI_ICON_SIZE[1] / 2)
        self.screen_render.image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def render_consumable_being_dragged(self, consumable_type: ConsumableType, mouse_screen_position: Tuple[int, int]):
        ui_icon_sprite = CONSUMABLES[consumable_type].icon_sprite
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] // 2, mouse_screen_position[1] - UI_ICON_SIZE[1] / 2)
        self.screen_render.image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def _splash_screen_text(self, text, x, y):
        self.screen_render.text(self.font_splash_screen, text, (x, y), COLOR_WHITE)
        self.screen_render.text(self.font_splash_screen, text, (x + 2, y + 2), COLOR_BLACK)

    def render_map_editor_ui(
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
        images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[sprite]
        image_with_relative_position = self._get_image_from_direction(images, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self.screen_render.image(image_with_relative_position.image, sprite_position)
        self.screen_render.rect((50, 250, 0), Rect(position[0], position[1], entity_size[0], entity_size[1]), 3)

    @staticmethod
    def update_display():
        pygame.display.update()

    def is_screen_position_within_ui(self, screen_position: Tuple[int, int]):
        ui_position = self._translate_screen_position_to_ui(screen_position)
        return ui_position[1] >= 0

    def render_picking_hero_ui(self, heroes: List[HeroId], selected_index: int):
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
            self.screen_render.text(self.font_dialog, hero.name, (x, y_0 + PORTRAIT_ICON_SIZE[1] + 10))
        description = HEROES[heroes[selected_index]].description
        description_lines = self._split_text_into_lines(description, 40)
        y_1 = 350
        for i, description_line in enumerate(description_lines):
            self.screen_render.text(self.font_dialog, description_line, (x_base, y_1 + i * 20))
        y_2 = 500
        self.screen_render.text(self.font_dialog, "SELECT YOUR HERO (Space to confirm)", (x_base, y_2))
