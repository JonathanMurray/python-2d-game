from typing import Dict, Any, List, Tuple, Optional, Union

import pygame

from pythongame.core.common import Direction, Sprite, ConsumableType, sum_of_vectors, ItemType, is_point_in_rect
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, SpriteInitializer, \
    ABILITIES, BUFF_TEXTS, Animation, KEYS_BY_ABILITY_TYPE, NON_PLAYER_CHARACTERS, CONSUMABLES, ITEMS, UiIconSprite, \
    WALLS, PORTRAIT_ICON_SPRITE_PATHS, PortraitIconSprite, NpcDialog
from pythongame.core.game_state import WorldEntity, DecorationEntity, NonPlayerCharacter
from pythongame.core.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText, VisualSprite
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
                 game_world_position: Optional[Tuple[int, int]]):
        self.item_slot_number = item_slot_number
        self.consumable_slot_number = consumable_slot_number
        self.game_world_position = game_world_position


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


class ImageWithRelativePosition:
    def __init__(self, image: Any, position_relative_to_entity: Tuple[int, int]):
        self.image = image
        self.position_relative_to_entity = position_relative_to_entity


# Used to display dialog from an npc along with the NPC's portrait
class DialogGraphics:
    def __init__(self, portrait_icon_sprite: PortraitIconSprite, npc_dialog: NpcDialog):
        self.portrait_icon_sprite = portrait_icon_sprite
        self.npc_dialog = npc_dialog


# Used to display some text above an NPC like "[Space] talk"
class EntityActionText:
    def __init__(self, entity: WorldEntity, text: str):
        self.entity = entity
        self.text = text


def load_and_scale_sprite(sprite_initializer: SpriteInitializer):
    image = pygame.image.load(sprite_initializer.image_file_path).convert_alpha()
    return pygame.transform.scale(image, sprite_initializer.scaling_size)


def load_and_scale_directional_sprites(
        animations_by_dir: Dict[Direction, Animation]) \
        -> Dict[Direction, List[ImageWithRelativePosition]]:
    images: Dict[Direction, List[ImageWithRelativePosition]] = {}
    for direction in animations_by_dir:
        animation = animations_by_dir[direction]
        images_for_dir: List[ImageWithRelativePosition] = []
        if animation.sprite_initializers:
            for sprite_init in animation.sprite_initializers:
                sprite_init: SpriteInitializer = sprite_init
                image = pygame.image.load(sprite_init.image_file_path).convert_alpha()
                scaled_image = pygame.transform.scale(image, sprite_init.scaling_size)
                images_for_dir.append(ImageWithRelativePosition(scaled_image, animation.position_relative_to_entity))
        elif animation.sprite_map_initializers:
            for sprite_map_init in animation.sprite_map_initializers:
                sprite_sheet = sprite_map_init.sprite_sheet
                index_position_within_map = sprite_map_init.index_position_within_map
                original_sprite_size = sprite_map_init.original_sprite_size
                rectangle = (index_position_within_map[0] * original_sprite_size[0],
                             index_position_within_map[1] * original_sprite_size[1],
                             original_sprite_size[0],
                             original_sprite_size[1])
                image = sprite_sheet.image_at(rectangle)
                scaled_image = pygame.transform.scale(image, sprite_map_init.scaling_size)
                images_for_dir.append(ImageWithRelativePosition(scaled_image, animation.position_relative_to_entity))
        else:
            raise Exception("Invalid animation: " + str(animation))
        images[direction] = images_for_dir
    return images


class View:

    def __init__(self, camera_size, screen_size):
        pygame.font.init()
        self.screen = pygame.display.set_mode(screen_size)
        self.ui_screen_area = ScreenArea((0, camera_size[1]), (screen_size[0], screen_size[1] - camera_size[1]))
        self.camera_size = camera_size
        self.screen_size = screen_size

        self.font_splash_screen = pygame.font.Font(DIR_FONTS + 'Arial Rounded Bold.ttf', 64)

        self.font_ui_stat_bar_numbers = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_ui_money = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 12)
        self.font_npc_action = pygame.font.Font(DIR_FONTS + 'Monaco.dfont', 14)
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
        self.font_dialog = pygame.font.Font(DIR_FONTS + 'Merchant Copy.ttf', 32)

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

        self.scaled_player_portrait = self.images_by_portrait_sprite[PortraitIconSprite.PLAYER]

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
    #           GENERAL DRAWING
    # ------------------------------------

    def _rect(self, color, rect, line_width):
        pygame.draw.rect(self.screen, color, rect, line_width)

    def _rect_filled(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)

    def _rect_transparent(self, rect, alpha, color):
        # Using a separate surface is the only way to render a transparent rectangle
        surface = pygame.Surface((rect[2], rect[3]))
        surface.set_alpha(alpha)
        surface.fill(color)
        self.screen.blit(surface, (rect[0], rect[1]))

    def _line(self, color, start_position, end_position, line_width):
        pygame.draw.line(self.screen, color, start_position, end_position, line_width)

    def _circle(self, color, position, radius, line_width):
        pygame.draw.circle(self.screen, color, position, radius, line_width)

    def _stat_bar(self, x, y, w, h, ratio_filled: float, color, border: bool):
        self._rect_filled((0, 0, 0), (x - 1, y - 1, w + 2, h + 2))
        if border:
            self._rect((250, 250, 250), (x - 2, y - 2, w + 4, h + 4), 1)
        self._rect_filled(color, (x, y, max(w * ratio_filled, 0), h))

    def _text(self, font, text, screen_pos, color=COLOR_WHITE):
        self.screen.blit(font.render(text, True, color), screen_pos)

    def _image(self, image, position):
        self.screen.blit(image, position)

    # ------------------------------------
    #       DRAWING THE GAME WORLD
    # ------------------------------------

    def _world_ground(self, game_world_size):
        grid_width = 35
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        column_screen_y_0 = self._translate_world_y_to_screen(max(0, self.camera_world_area.y))
        column_screen_y_1 = self._translate_world_y_to_screen(
            min(game_world_size[1], self.camera_world_area.y + self.camera_world_area.h))
        for col in range(num_squares):
            world_x = col * grid_width
            if 0 < world_x < game_world_size[0]:
                screen_x = self._translate_world_x_to_screen(world_x)
                self._line(COLOR_BACKGROUND_LINES, (screen_x, column_screen_y_0), (screen_x, column_screen_y_1), 1)
        row_screen_x_0 = self._translate_world_x_to_screen(max(0, self.camera_world_area.x))
        row_screen_x_1 = self._translate_world_x_to_screen(
            min(game_world_size[0], self.camera_world_area.x + self.camera_world_area.w))
        for row in range(num_squares):
            world_y = row * grid_width
            if 0 < world_y < game_world_size[1]:
                screen_y = self._translate_world_y_to_screen(world_y)
                self._line(COLOR_BACKGROUND_LINES, (row_screen_x_0, screen_y), (row_screen_x_1, screen_y), 1)

        if RENDER_WORLD_COORDINATES:
            for col in range(num_squares):
                for row in range(num_squares):
                    if col % 4 == 0 and row % 4 == 0:
                        world_x = col * grid_width
                        screen_x = self._translate_world_x_to_screen(world_x)
                        world_y = row * grid_width
                        screen_y = self._translate_world_y_to_screen(world_y)
                        self._text(self.font_debug_info, str(world_x) + "," + str(world_y), (screen_x, screen_y),
                                   (250, 250, 250))

    def _world_rect(self, color, world_rect, line_width=0):
        translated_pos = self._translate_world_position_to_screen((world_rect[0], world_rect[1]))
        self._rect(color, (translated_pos[0], translated_pos[1], world_rect[2], world_rect[3]), line_width)

    def _world_entity(self, entity: Union[WorldEntity, DecorationEntity]):
        if entity.sprite is None:
            raise Exception("Entity has no sprite: " + str(entity))
        elif entity.sprite in self.images_by_sprite:
            images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[entity.sprite]
            image_with_relative_position = self._get_image_from_direction(images, entity.direction,
                                                                          entity.movement_animation_progress)
            pos = self._translate_world_position_to_screen((entity.x, entity.y))
            pos = sum_of_vectors(pos, image_with_relative_position.position_relative_to_entity)
            self._image(image_with_relative_position.image, pos)
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
        elif isinstance(visual_effect, VisualText):
            self._visual_text(visual_effect)
        elif isinstance(visual_effect, VisualSprite):
            self._visual_sprite(visual_effect)
        else:
            raise Exception("Unhandled visual effect: " + str(visual_effect))

    def _visual_line(self, line: VisualLine):
        start_position = self._translate_world_position_to_screen(line.start_position)
        end_position = self._translate_world_position_to_screen(line.end_position)
        self._line(line.color, start_position, end_position, line.line_width)

    def _visual_circle(self, visual_circle: VisualCircle):
        position = visual_circle.circle()[0]
        radius = visual_circle.circle()[1]
        translated_position = self._translate_world_position_to_screen(position)
        self._circle(visual_circle.color, translated_position, radius, visual_circle.line_width)

    def _visual_rect(self, visual_rect: VisualRect):
        self._world_rect(visual_rect.color, visual_rect.rect(), visual_rect.line_width)

    def _visual_text(self, visual_text: VisualText):
        position = visual_text.position()
        translated_position = self._translate_world_position_to_screen(position)
        self._text(self.font_game_world_text, visual_text.text, translated_position, visual_text.color)

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
            self._image(image_with_relative_position.image, pos)
        else:
            raise Exception("Unhandled sprite: " + str(sprite))

    def _stat_bar_for_world_entity(self, world_entity, h, relative_y, stat, max_stat, color):
        position_on_screen = self._translate_world_position_to_screen((world_entity.x, world_entity.y))
        self._stat_bar(position_on_screen[0] + 1, position_on_screen[1] + relative_y,
                       world_entity.w - 2, h, stat / max_stat, color, False)

    # ------------------------------------
    #           DRAWING THE UI
    # ------------------------------------

    def _stat_bar_in_ui(self, position_in_ui, w, h, ratio_filled: float, color, border: bool):
        x, y = self._translate_ui_position_to_screen(position_in_ui)
        self._stat_bar(x, y, w, h, ratio_filled, color, border)

    def _consumable_icon_in_ui(self, x_in_ui, y_in_ui, size, consumable_number, consumable_type: ConsumableType,
                               highlighted_consumable_action):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self._rect_filled((40, 40, 50), (x, y, w, h))
        if consumable_type:
            icon_sprite = CONSUMABLES[consumable_type].icon_sprite
            self._image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._rect((150, 150, 190), (x, y, w, h), 1)
        if highlighted_consumable_action == consumable_number:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_ui_icon_keys, str(consumable_number), (x + 12, y + h + 4))

    def _ability_icon_in_ui(self, x_in_ui, y_in_ui, size, ability_type, highlighted_ability_action,
                            ability_cooldowns_remaining):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        ability = ABILITIES[ability_type]
        ability_key = KEYS_BY_ABILITY_TYPE[ability_type]
        icon_sprite = ability.icon_sprite
        self._rect_filled((40, 40, 50), (x, y, w, h))
        self._image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._rect((150, 150, 190), (x, y, w, h), 1)
        if highlighted_ability_action == ability_type:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_ui_icon_keys, ability_key.key_string, (x + 12, y + h + 4))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / ability.cooldown
            cooldown_rect = (x + 2, y + 2 + (h - 4) * (1 - ratio_remaining), w - 4, (h - 4) * ratio_remaining + 2)
            self._rect_filled((100, 30, 30), cooldown_rect)

    def _item_icon_in_ui(self, x_in_ui, y_in_ui, size, item_type: ItemType):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self._rect_filled((40, 40, 50), (x, y, w, h))
        if item_type:
            ui_icon_sprite = ITEMS[item_type].icon_sprite
            self._image(self.images_by_ui_sprite[ui_icon_sprite], (x, y))
        self._rect((150, 150, 190), (x, y, w, h), 1)

    def _map_editor_icon_in_ui(self, x_in_ui, y_in_ui, size, highlighted: bool, user_input_key: str,
                               entity: Optional[MapEditorWorldEntity], non_entity_icon: Optional[UiIconSprite]):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))

        self._rect_filled((40, 40, 40), (x, y, w, h))

        if entity:
            if entity.npc_type:
                npc_data = NON_PLAYER_CHARACTERS[entity.npc_type]
                image = self.images_by_sprite[npc_data.sprite][Direction.DOWN][0].image
            elif entity.consumable_type:
                ui_icon_sprite = CONSUMABLES[entity.consumable_type].icon_sprite
                image = self.images_by_ui_sprite[ui_icon_sprite]
            elif entity.is_player:
                image = self.images_by_sprite[Sprite.PLAYER][Direction.DOWN][0].image
            elif entity.wall_type:
                wall_data = WALLS[entity.wall_type]
                image = self.images_by_sprite[wall_data.sprite][Direction.DOWN][0].image
            elif entity.item_type:
                ui_icon_sprite = ITEMS[entity.item_type].icon_sprite
                image = self.images_by_ui_sprite[ui_icon_sprite]
            elif entity.decoration_sprite:
                image = self.images_by_sprite[entity.decoration_sprite][Direction.DOWN][0].image
            elif entity.money_amount:
                # TODO handle other amounts of money
                image = self.images_by_sprite[Sprite.COINS_5][Direction.DOWN][0].image
            else:
                raise Exception("Unknown entity: " + str(entity))
        else:
            image = self.images_by_ui_sprite[non_entity_icon]

        icon_scaled_image = pygame.transform.scale(image, size)
        self._image(icon_scaled_image, (x, y))

        self._rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_ui_icon_keys, user_input_key, (x + 12, y + h + 4))

    def _rect_in_ui(self, color, rect, line_width):
        translated_rect = (self._translate_ui_x_to_screen(rect[0]), self._translate_ui_y_to_screen(rect[1]),
                           rect[2], rect[3])
        self._rect(color, translated_rect, line_width)

    def _image_in_ui(self, image, position):
        self._image(image, self._translate_ui_position_to_screen(position))

    def _text_in_ui(self, font, text, ui_pos, color=COLOR_WHITE):
        screen_pos = self._translate_ui_position_to_screen((ui_pos))
        self._text(font, text, screen_pos, color)

    def _minimap_in_ui(self, position_in_ui, size, player_relative_position):
        pos_in_screen = self._translate_ui_position_to_screen(position_in_ui)
        rect_in_screen = (pos_in_screen[0], pos_in_screen[1], size[0], size[1])
        self._rect_filled((40, 40, 50), rect_in_screen)
        self._rect((150, 150, 190), rect_in_screen, 1)
        dot_x = rect_in_screen[0] + player_relative_position[0] * size[0]
        dot_y = rect_in_screen[1] + player_relative_position[1] * size[1]
        dot_w = 4
        self._rect_filled((100, 160, 100), (dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))

    def _message(self, message):
        x_message = self.ui_screen_area.w / 2 - 140
        y_message = self.ui_screen_area.y - 30
        self._rect_transparent((x_message - 10, y_message - 5, 280, 28), 85, (0, 0, 0))
        self._text(self.font_message, message, (x_message, y_message))

    def _tooltip(self, title: str, details: List[str], position_bottom_left: Tuple[int, int]):
        w_tooltip = 320
        h_tooltip = 130
        x_tooltip = position_bottom_left[0]
        y_tooltip = position_bottom_left[1] - h_tooltip
        rect_tooltip = (x_tooltip, y_tooltip, w_tooltip, h_tooltip)
        self._rect_transparent((x_tooltip, y_tooltip, w_tooltip, h_tooltip), 240, (0, 0, 30))
        self._rect(COLOR_WHITE, rect_tooltip, 2)
        self._text(self.font_tooltip_header, title, (x_tooltip + 20, y_tooltip + 15), COLOR_WHITE)
        y_separator = y_tooltip + 40
        self._line(COLOR_WHITE, (x_tooltip + 10, y_separator), (x_tooltip + w_tooltip - 10, y_separator), 1)
        for i, detail in enumerate(details):
            self._text(self.font_tooltip_details, detail, (x_tooltip + 20, y_tooltip + 50 + i * 20), COLOR_WHITE)

    def _entity_action_text(self, entity_action_text: EntityActionText):
        npc_center_pos = self._translate_world_position_to_screen(
            entity_action_text.entity.get_center_position())
        rect_width = 120
        rect_height = 27
        rect_pos = (npc_center_pos[0] - rect_width / 2, npc_center_pos[1] - 60)
        self._rect_transparent((rect_pos[0], rect_pos[1], rect_width, rect_height), 150, (0, 0, 0))
        self._text(self.font_npc_action, entity_action_text.text, (rect_pos[0] + 10, rect_pos[1] + 4))

    def render_world(self, all_entities_to_render: List[WorldEntity], decorations_to_render: List[DecorationEntity],
                     camera_world_area, non_player_characters: List[NonPlayerCharacter], is_player_invisible,
                     player_entity, visual_effects, render_hit_and_collision_boxes, player_health, player_max_health,
                     game_world_size, entity_action_text: Optional[EntityActionText]):
        self.camera_world_area = camera_world_area

        self.screen.fill(COLOR_BACKGROUND)
        self._world_ground(game_world_size)

        all_entities_to_render.sort(key=lambda entry: entry.y)

        for decoration_entity in decorations_to_render:
            self._world_entity(decoration_entity)

        for entity in all_entities_to_render:
            if entity == player_entity and is_player_invisible:
                self._world_rect((200, 100, 250), player_entity.rect(), 1)
            else:
                self._world_entity(entity)

        self._stat_bar_for_world_entity(player_entity, 5, -35, player_health, player_max_health, (100, 200, 0))

        if render_hit_and_collision_boxes:
            for entity in all_entities_to_render:
                # hit box
                self._world_rect((250, 250, 250), entity.rect(), 1)

        for npc in non_player_characters:
            color = COLOR_RED if npc.is_enemy else (250, 250, 0)
            if not npc.is_neutral:
                self._stat_bar_for_world_entity(npc.world_entity, 5, -10, npc.health, npc.max_health, color)
            if npc.active_buffs:
                buff = npc.active_buffs[0]
                if buff.total_duration > 1000:
                    self._stat_bar_for_world_entity(npc.world_entity, 2, -14, buff.time_until_expiration,
                                                    buff.total_duration, (250, 250, 250))
        for visual_effect in visual_effects:
            self._visual_effect(visual_effect)

        if entity_action_text:
            self._entity_action_text(entity_action_text)

    def render_ui(self, fps_string, is_paused, is_game_over, abilities, ability_cooldowns_remaining,
                  highlighted_ability_action, highlighted_consumable_action, message: str, player_active_buffs,
                  player_health, player_mana, player_max_health, player_max_mana, player_health_regen: float,
                  player_mana_regen: float, player_speed_multiplier: float, player_life_steal: float,
                  player_minimap_relative_position, consumable_slots, item_slots: Dict[int, ItemType],
                  player_level: int, mouse_screen_position: Tuple[int, int], player_exp: int,
                  player_max_exp_in_this_level: int, dialog: Optional[DialogGraphics], player_money: int,
                  player_damage_modifier: float) -> MouseHoverEvent:

        hovered_item_slot_number = None
        hovered_consumable_slot_number = None
        is_mouse_hovering_ui = is_point_in_rect(
            mouse_screen_position,
            (self.ui_screen_area.x, self.ui_screen_area.y, self.ui_screen_area.w, self.ui_screen_area.h))

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)
        tooltip_title = ""
        tooltip_details = []
        tooltip_bottom_left_position = (175, 450)

        self._rect(COLOR_BORDER, (0, 0, self.camera_size[0], self.camera_size[1]), 1)
        self._rect_filled((20, 10, 0), (0, self.camera_size[1], self.screen_size[0],
                                        self.screen_size[1] - self.camera_size[1]))

        y_0 = 5

        y_1 = 30
        y_2 = y_1 + 22
        y_3 = 90
        y_4 = y_3 + 22

        x_1 = 140

        x_exp_bar = x_1
        self._text_in_ui(self.font_level, "Level " + str(player_level), (x_exp_bar, y_0))
        self._stat_bar_in_ui((x_exp_bar, y_0 + 18), 380, 2, player_exp / player_max_exp_in_this_level, (200, 200, 200),
                             True)

        x_0 = 20

        # TODO: Extract this code
        rect_portrait_pos = self._translate_ui_position_to_screen((x_0, y_0 + 13))
        self._image(self.scaled_player_portrait, rect_portrait_pos)
        self._rect((160, 160, 180), (rect_portrait_pos[0], rect_portrait_pos[1], 100, 70), 2)

        rect_healthbar = (x_0, y_4 - 1, 100, 14)
        self._stat_bar_in_ui((rect_healthbar[0], rect_healthbar[1]), rect_healthbar[2], rect_healthbar[3],
                             player_health / player_max_health, (200, 0, 50), True)
        if is_point_in_rect(mouse_ui_position, rect_healthbar):
            tooltip_title = "Health"
            tooltip_details = ["regeneration: " + "{:.1f}".format(player_health_regen) + "/s"]
            tooltip_details += ["damage bonus: +" + str(int(round((player_damage_modifier - 1) * 100))) + "%"]
            tooltip_bottom_left_position = self._translate_ui_position_to_screen((rect_healthbar[0], rect_healthbar[1]))
        health_text = str(player_health) + "/" + str(player_max_health)
        self._text_in_ui(self.font_ui_stat_bar_numbers, health_text, (x_0 + 20, y_4 - 1))

        rect_manabar = (x_0, y_4 + 20, 100, 14)
        self._stat_bar_in_ui((rect_manabar[0], rect_manabar[1]), rect_manabar[2], rect_manabar[3],
                             player_mana / player_max_mana, (50, 0, 200), True)
        if is_point_in_rect(mouse_ui_position, rect_manabar):
            tooltip_title = "Mana"
            tooltip_details = ["regeneration: " + "{:.1f}".format(player_mana_regen) + "/s"]
            tooltip_bottom_left_position = self._translate_ui_position_to_screen((rect_manabar[0], rect_manabar[1]))
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._text_in_ui(self.font_ui_stat_bar_numbers, mana_text, (x_0 + 20, y_4 + 20))

        self._text_in_ui(self.font_ui_money, "Money: " + str(player_money), (x_0 + 4, y_4 + 38))

        # CONSUMABLES
        icon_space = 2
        icon_rect_padding = 2
        consumables_rect_pos = self._translate_ui_position_to_screen((x_1 - icon_rect_padding, y_2 - icon_rect_padding))
        consumables_rect = (
            consumables_rect_pos[0], consumables_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * len(consumable_slots) - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self._rect_filled((60, 60, 80), consumables_rect)
        for i, slot_number in enumerate(consumable_slots):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            consumable_type = consumable_slots[slot_number]
            if is_point_in_rect(mouse_ui_position, (x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                hovered_consumable_slot_number = slot_number
                if consumable_type:
                    tooltip_title = CONSUMABLES[consumable_type].name
                    tooltip_details = [CONSUMABLES[consumable_type].description]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
            self._consumable_icon_in_ui(x, y, UI_ICON_SIZE, slot_number,
                                        consumable_type, highlighted_consumable_action)

        # ABILITIES
        abilities_rect_pos = self._translate_ui_position_to_screen((x_1 - icon_rect_padding, y_4 - icon_rect_padding))
        max_num_abilities = 5
        abilities_rect = (
            abilities_rect_pos[0], abilities_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * max_num_abilities - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self._rect_filled((60, 60, 80), abilities_rect)
        for i, ability_type in enumerate(abilities):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_4
            if is_point_in_rect(mouse_ui_position, (x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                if ability_type:
                    ability_data = ABILITIES[ability_type]
                    tooltip_title = ability_data.name
                    cooldown = str(ability_data.cooldown / 1000.0)
                    mana_cost = str(ability_data.mana_cost)
                    tooltip_details = ["Cooldown: " + cooldown + " s", "Mana: " + mana_cost, ability_data.description]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
            self._ability_icon_in_ui(x, y, UI_ICON_SIZE, ability_type,
                                     highlighted_ability_action, ability_cooldowns_remaining)

        # ITEMS
        x_2 = 326
        items_rect_pos = self._translate_ui_position_to_screen((x_2 - icon_rect_padding, y_2 - icon_rect_padding))
        items_rect = (
            items_rect_pos[0], items_rect_pos[1],
            (UI_ICON_SIZE[0] + icon_space) * len(item_slots) - icon_space + icon_rect_padding * 2,
            UI_ICON_SIZE[1] + icon_rect_padding * 2)
        self._rect_filled((60, 60, 80), items_rect)
        for i, item_slot_number in enumerate(item_slots.keys()):
            x = x_2 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            item_type = item_slots[item_slot_number]
            if is_point_in_rect(mouse_ui_position, (x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                hovered_item_slot_number = item_slot_number
                if item_type:
                    tooltip_title = ITEMS[item_type].name
                    tooltip_details = [ITEMS[item_type].description]
                    tooltip_bottom_left_position = self._translate_ui_position_to_screen((x, y))
            self._item_icon_in_ui(x, y, UI_ICON_SIZE, item_type)

        # MINIMAP
        x_3 = 440
        minimap_padding_rect_pos = self._translate_ui_position_to_screen((x_3 - 2, y_2 - 2))
        minimap_padding_rect = (minimap_padding_rect_pos[0], minimap_padding_rect_pos[1], 80 + 4, 80 + 4)
        self._rect_filled((60, 60, 80), minimap_padding_rect)
        self._minimap_in_ui((x_3, y_2), (80, 80), player_minimap_relative_position)

        if dialog:
            self._dialog(dialog)

        # BUFFS
        x_buffs = 22
        buff_texts = []
        buff_duration_ratios_remaining = []
        for active_buff in player_active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            # Buffs that don't have description texts shouldn't be displayed. (They are typically irrelevant to the
            # player)
            if buff_type in BUFF_TEXTS:
                ratio_duration_remaining = active_buff.time_until_expiration / active_buff.total_duration
                buff_texts.append(BUFF_TEXTS[buff_type])
                buff_duration_ratios_remaining.append(ratio_duration_remaining)
        for i, text in enumerate(buff_texts):
            self._text_in_ui(self.font_buff_texts, text, (x_buffs, -40 + i * 25))
            self._stat_bar_in_ui((x_buffs, -20 + i * 25), 60, 2, buff_duration_ratios_remaining[i], (250, 250, 0),
                                 False)

        # STATS
        x_stats = 555
        health_regen_text = \
            "health reg: " + "{:.1f}".format(player_health_regen) + "/s"
        mana_regen_text = \
            "  mana reg: " + "{:.1f}".format(player_mana_regen) + "/s"
        damage_stat_text = \
            "    damage: +" + str(int(round((player_damage_modifier - 1) * 100))) + "%"
        speed_stat_text = \
            "     speed: +" + str(int(round((player_speed_multiplier - 1) * 100))) + "%"
        lifesteal_stat_text = \
            "life steal: " + str(int(round(player_life_steal * 100))) + "%"
        self._text_in_ui(self.font_stats, health_regen_text, (x_stats, y_1), COLOR_WHITE)
        self._text_in_ui(self.font_stats, mana_regen_text, (x_stats, y_1 + 20), COLOR_WHITE)
        self._text_in_ui(self.font_stats, damage_stat_text, (x_stats, y_1 + 40), COLOR_WHITE)
        self._text_in_ui(self.font_stats, speed_stat_text, (x_stats, y_1 + 60), COLOR_WHITE)
        self._text_in_ui(self.font_stats, lifesteal_stat_text, (x_stats, y_1 + 80), COLOR_WHITE)

        self._rect(COLOR_BORDER, self.ui_screen_area.rect(), 1)

        self._rect_transparent((0, 0, 50, 20), 100, COLOR_BLACK)
        self._text(self.font_debug_info, fps_string + " fps", (5, 3))

        if message:
            self._message(message)

        if tooltip_title:
            self._tooltip(tooltip_title, tooltip_details, tooltip_bottom_left_position)

        if is_game_over:
            self._splash_screen_text("You died!", self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50)
        elif is_paused:
            self._rect_transparent((0, 0, self.screen_size[0], self.screen_size[1]), 140, COLOR_BLACK)
            self._splash_screen_text("PAUSED", self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50)

        mouse_game_world_position = None
        if not is_mouse_hovering_ui:
            mouse_game_world_position = self._translate_screen_position_to_world(mouse_screen_position)
        return MouseHoverEvent(hovered_item_slot_number, hovered_consumable_slot_number, mouse_game_world_position)

    def _dialog(self, dialog_graphics: DialogGraphics):
        rect_dialog_container = (100, 75, 500, 250)
        self._rect((210, 180, 60), rect_dialog_container, 5)
        self._rect_transparent(rect_dialog_container, 180, COLOR_BLACK)
        lower_boundary_y = 280
        self._line((170, 140, 20), (100, lower_boundary_y), (600, lower_boundary_y), 2)
        dialog_container_portrait_padding = 10
        rect_portrait_pos = (rect_dialog_container[0] + dialog_container_portrait_padding,
                             rect_dialog_container[1] + dialog_container_portrait_padding)
        dialog_image = self.images_by_portrait_sprite[dialog_graphics.portrait_icon_sprite]
        self._image(dialog_image, rect_portrait_pos)
        self._rect((160, 160, 180), (rect_portrait_pos[0], rect_portrait_pos[1], 100, 70), 2)
        dialog_pos = (rect_dialog_container[0] + 120, rect_dialog_container[1] + 15)
        dialog_lines = self._split_text_into_lines(dialog_graphics.npc_dialog.body, 33)
        for i, dialog_text_line in enumerate(dialog_lines):
            if i == 6:
                print("WARN: too long dialog for NPC!")
                break
            self._text(self.font_dialog, dialog_text_line, (dialog_pos[0] + 5, dialog_pos[1] + 32 * i),
                       COLOR_WHITE)
        self._text(self.font_dialog, "[Space] " + dialog_graphics.npc_dialog.action,
                   (rect_dialog_container[0] + 65, dialog_pos[1] + 202),
                   COLOR_WHITE)

    @staticmethod
    def _split_text_into_lines(full_text: str, max_line_length: int):
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
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] / 2, mouse_screen_position[1] - UI_ICON_SIZE[1] / 2)
        self._image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def render_consumable_being_dragged(self, consumable_type: ConsumableType, mouse_screen_position: Tuple[int, int]):
        ui_icon_sprite = CONSUMABLES[consumable_type].icon_sprite
        position = (mouse_screen_position[0] - UI_ICON_SIZE[0] / 2, mouse_screen_position[1] - UI_ICON_SIZE[1] / 2)
        self._image(self.images_by_ui_sprite[ui_icon_sprite], position)

    def _splash_screen_text(self, text, x, y):
        self._text(self.font_splash_screen, text, (x, y), COLOR_WHITE)
        self._text(self.font_splash_screen, text, (x + 2, y + 2), COLOR_BLACK)

    def render_map_editor_ui(
            self, chars_by_entities: Dict[MapEditorWorldEntity, str], entities: List[MapEditorWorldEntity],
            placing_entity: Optional[MapEditorWorldEntity], deleting_entities: bool, deleting_decorations: bool,
            num_enemies: int, num_walls: int, num_decorations: int, grid_cell_size: int,
            mouse_screen_position: Tuple[int, int]) -> Optional[MapEditorWorldEntity]:

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)

        hovered_by_mouse: MapEditorWorldEntity = None

        self._rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._rect_filled(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                        self.screen_size[1] - self.camera_size[1]))

        icon_space = 5

        y_1 = 17
        y_2 = y_1 + 22
        y_3 = y_2 + MAP_EDITOR_UI_ICON_SIZE[1] + 25

        x_0 = 20
        self._map_editor_icon_in_ui(x_0, y_2, MAP_EDITOR_UI_ICON_SIZE, deleting_entities, 'Q', None,
                                    UiIconSprite.MAP_EDITOR_TRASHCAN)
        self._map_editor_icon_in_ui(x_0 + MAP_EDITOR_UI_ICON_SIZE[0] + icon_space, y_2, MAP_EDITOR_UI_ICON_SIZE,
                                    deleting_decorations, 'Z', None, UiIconSprite.MAP_EDITOR_RECYCLING)

        x_1 = 155
        self._text_in_ui(self.font_ui_headers, "ENTITIES", (x_1, y_1))
        num_icons_per_row = 27
        for i, entity in enumerate(entities):
            if entity in chars_by_entities:
                char = chars_by_entities[entity]
            else:
                char = ''
            is_this_entity_being_placed = entity is placing_entity
            x = x_1 + (i % num_icons_per_row) * (MAP_EDITOR_UI_ICON_SIZE[0] + icon_space)
            y = y_2 if i < num_icons_per_row else y_3
            if is_point_in_rect(mouse_ui_position, (x, y, MAP_EDITOR_UI_ICON_SIZE[0], MAP_EDITOR_UI_ICON_SIZE[1])):
                hovered_by_mouse = entity
            self._map_editor_icon_in_ui(x, y, MAP_EDITOR_UI_ICON_SIZE, is_this_entity_being_placed, char, entity, None)

        self._rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

        self._rect_transparent((0, 0, 150, 80), 100, COLOR_BLACK)
        self._text(self.font_debug_info, "# enemies: " + str(num_enemies), (5, 3))
        self._text(self.font_debug_info, "# walls: " + str(num_walls), (5, 20))
        self._text(self.font_debug_info, "# decorations: " + str(num_decorations), (5, 37))
        self._text(self.font_debug_info, "Cell size: " + str(grid_cell_size), (5, 54))

        return hovered_by_mouse

    def render_map_editor_mouse_rect(self, color: Tuple[int, int, int],
                                     map_editor_mouse_rect: Tuple[int, int, int, int]):
        self._rect(color, map_editor_mouse_rect, 3)

    def render_map_editor_world_entity_at_position(self, entity: WorldEntity, position: Tuple[int, int]):
        images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[entity.sprite]
        image_with_relative_position = self._get_image_from_direction(images, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self._image(image_with_relative_position.image, sprite_position)
        self._rect((50, 250, 0), (position[0], position[1], entity.w, entity.h), 3)

    @staticmethod
    def update_display():
        pygame.display.update()

    def is_screen_position_within_ui(self, screen_position: Tuple[int, int]):
        ui_position = self._translate_screen_position_to_ui(screen_position)
        return ui_position[1] >= 0
