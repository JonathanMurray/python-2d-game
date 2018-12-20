from typing import Dict, Any, List, Tuple, Optional

import pygame

from pythongame.core.common import Direction, Sprite, PotionType, sum_of_vectors, ItemType, is_point_in_rect
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, SpriteInitializer, \
    ABILITIES, BUFF_TEXTS, Animation, USER_ABILITY_KEYS, ENEMIES, POTIONS, ITEMS
from pythongame.core.game_state import WorldEntity
from pythongame.core.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText, VisualSprite
from pythongame.game_world_init import MapFileEntity

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
UI_ICON_SIZE = (32, 32)
MAP_EDITOR_UI_ICON_SIZE = (48, 48)

RENDER_WORLD_COORDINATES = False


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
        self.font_huge = pygame.font.SysFont('Arial', 64)
        self.font_large = pygame.font.SysFont('Arial', 22)
        self.font_small = pygame.font.Font(None, 25)
        self.font_tiny = pygame.font.Font(None, 19)
        self.images_by_sprite: Dict[Sprite, Dict[Direction, List[ImageWithRelativePosition]]] = {
            sprite: load_and_scale_directional_sprites(ENTITY_SPRITE_INITIALIZERS[sprite])
            for sprite in ENTITY_SPRITE_INITIALIZERS
        }
        self.images_by_ui_sprite = {sprite: load_and_scale_sprite(
            SpriteInitializer(UI_ICON_SPRITE_PATHS[sprite], UI_ICON_SIZE))
            for sprite in UI_ICON_SPRITE_PATHS}

        # This is updated every time the view is called
        self.camera_world_area = None

    # ------------------------------------
    #         TRANSLATING COORDINATES
    # ------------------------------------

    def _translate_world_position_to_screen(self, world_position):
        return (self._translate_world_x_to_screen(world_position[0]),
                self._translate_world_y_to_screen(world_position[1]))

    def _translate_world_x_to_screen(self, world_x):
        return int(world_x - self.camera_world_area.x)

    def _translate_world_y_to_screen(self, world_y):
        return int(world_y - self.camera_world_area.y)

    def _translate_ui_position_to_screen(self, position):
        return position[0] + self.ui_screen_area.x, position[1] + self.ui_screen_area.y

    def _translate_screen_position_to_ui(self, position: Tuple[int, int]):
        return position[0] - self.ui_screen_area.x, position[1] - self.ui_screen_area.y

    # ------------------------------------
    #           GENERAL DRAWING
    # ------------------------------------

    def _rect(self, color, rect, line_width):
        pygame.draw.rect(self.screen, color, rect, line_width)

    def _rect_filled(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)

    def _line(self, color, start_position, end_position, line_width):
        pygame.draw.line(self.screen, color, start_position, end_position, line_width)

    def _circle(self, color, position, radius, line_width):
        pygame.draw.circle(self.screen, color, position, radius, line_width)

    def _stat_bar(self, x, y, w, h, stat, max_stat, color, border):
        self._rect_filled((0, 0, 0), (x - 1, y - 1, w + 2, h + 2))
        if border:
            self._rect((250, 250, 250), (x - 2, y - 2, w + 4, h + 4), 2)
        self._rect_filled(color, (x, y, max(w * stat / max_stat, 0), h))

    def _text(self, font, text, screen_pos, color=COLOR_WHITE):
        self.screen.blit(font.render(text, False, color), screen_pos)

    def _image(self, image, position):
        self.screen.blit(image, position)

    # ------------------------------------
    #       DRAWING THE GAME WORLD
    # ------------------------------------

    def _world_ground(self, game_world_size):
        line_color = (190, 190, 200)
        grid_width = 50
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        column_screen_y_0 = self._translate_world_y_to_screen(max(0, self.camera_world_area.y))
        column_screen_y_1 = self._translate_world_y_to_screen(
            min(game_world_size[1], self.camera_world_area.y + self.camera_world_area.h))
        for col in range(num_squares):
            world_x = col * grid_width
            if 0 < world_x < game_world_size[0]:
                screen_x = self._translate_world_x_to_screen(world_x)
                self._line(line_color, (screen_x, column_screen_y_0), (screen_x, column_screen_y_1), 1)
        row_screen_x_0 = self._translate_world_x_to_screen(max(0, self.camera_world_area.x))
        row_screen_x_1 = self._translate_world_x_to_screen(
            min(game_world_size[0], self.camera_world_area.x + self.camera_world_area.w))
        for row in range(num_squares):
            world_y = row * grid_width
            if 0 < world_y < game_world_size[1]:
                screen_y = self._translate_world_y_to_screen(world_y)
                self._line(line_color, (row_screen_x_0, screen_y), (row_screen_x_1, screen_y), 1)

        if RENDER_WORLD_COORDINATES:
            for col in range(num_squares):
                for row in range(num_squares):
                    if col % 4 == 0 and row % 4 == 0:
                        world_x = col * grid_width
                        screen_x = self._translate_world_x_to_screen(world_x)
                        world_y = row * grid_width
                        screen_y = self._translate_world_y_to_screen(world_y)
                        self._text(self.font_tiny, str(world_x) + "," + str(world_y), (screen_x, screen_y),
                                   (250, 250, 250))

    def _world_rect(self, color, world_rect, line_width=0):
        translated_pos = self._translate_world_position_to_screen((world_rect[0], world_rect[1]))
        self._rect(color, (translated_pos[0], translated_pos[1], world_rect[2], world_rect[3]), line_width)

    def _world_entity(self, entity: WorldEntity):
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

    def _visual_line(self, line):
        start_position = self._translate_world_position_to_screen(line.start_position)
        end_position = self._translate_world_position_to_screen(line.end_position)
        self._line(line.color, start_position, end_position, line.line_width)

    def _visual_circle(self, visual_circle):
        position = visual_circle.circle()[0]
        radius = visual_circle.circle()[1]
        translated_position = self._translate_world_position_to_screen(position)
        self._circle(visual_circle.color, translated_position, radius, visual_circle.line_width)

    def _visual_rect(self, visual_rect):
        self._world_rect(visual_rect.color, visual_rect.rect(), visual_rect.line_width)

    def _visual_text(self, visual_effect):
        position = visual_effect.position()
        translated_position = self._translate_world_position_to_screen(position)
        self._text(self.font_tiny, visual_effect.text, translated_position, visual_effect.color)

    def _visual_sprite(self, visual_sprite):
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
                       world_entity.w - 2, h, stat, max_stat, color, False)

    # ------------------------------------
    #           DRAWING THE UI
    # ------------------------------------

    def _stat_bar_in_ui(self, position_in_ui, w, h, stat, max_stat, color):
        x, y = self._translate_ui_position_to_screen(position_in_ui)
        self._stat_bar(x, y, w, h, stat, max_stat, color, True)

    def _potion_icon_in_ui(self, x_in_ui, y_in_ui, size, potion_number, potion_type: PotionType,
                           highlighted_potion_action):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self._rect_filled((40, 40, 40), (x, y, w, h))
        if potion_type:
            icon_sprite = POTIONS[potion_type].icon_sprite
            self._image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted_potion_action == potion_number:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_tiny, str(potion_number), (x + 8, y + h + 4))

    def _ability_icon_in_ui(self, x_in_ui, y_in_ui, size, ability_type, highlighted_ability_action,
                            ability_cooldowns_remaining):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        ability = ABILITIES[ability_type]
        ability_key = USER_ABILITY_KEYS[ability_type]
        mana_cost = ability.mana_cost
        icon_sprite = ability.icon_sprite
        self._rect_filled((40, 40, 40), (x, y, w, h))
        self._image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted_ability_action == ability_type:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_tiny, ability_key.key_string, (x + 8, y + h + 4))
        self._text(self.font_tiny, str(mana_cost), (x + 8, y + h + 19))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / ability.cooldown
            cooldown_rect = (x + 2, y + 2 + (h - 4) * (1 - ratio_remaining), w - 4, (h - 4) * ratio_remaining + 2)
            self._rect_filled((100, 30, 30), cooldown_rect)

    def _item_icon_in_ui(self, x_in_ui, y_in_ui, size, item_type: ItemType):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self._rect_filled((40, 40, 40), (x, y, w, h))
        if item_type:
            ui_icon_sprite = ITEMS[item_type].icon_sprite
            self._image(self.images_by_ui_sprite[ui_icon_sprite], (x, y))
        self._rect(COLOR_WHITE, (x, y, w, h), 2)

    def _map_editor_icon_in_ui(self, x_in_ui, y_in_ui, size, highlighted: bool, user_input_key: str,
                               map_file_entity: MapFileEntity):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))

        self._rect_filled((40, 40, 40), (x, y, w, h))

        if map_file_entity.enemy_type:
            enemy_data = ENEMIES[map_file_entity.enemy_type]
            image = self.images_by_sprite[enemy_data.sprite][Direction.DOWN][0].image
        elif map_file_entity.potion_type:
            ui_icon_sprite = POTIONS[map_file_entity.potion_type].icon_sprite
            image = self.images_by_ui_sprite[ui_icon_sprite]
        elif map_file_entity.is_player:
            image = self.images_by_sprite[Sprite.PLAYER][Direction.DOWN][0].image
        elif map_file_entity.is_wall:
            image = self.images_by_sprite[Sprite.WALL][Direction.DOWN][0].image
        elif map_file_entity.item_type:
            ui_icon_sprite = ITEMS[map_file_entity.item_type].icon_sprite
            image = self.images_by_ui_sprite[ui_icon_sprite]
        else:
            raise Exception("Unknown entity: " + str(map_file_entity))

        icon_scaled_image = pygame.transform.scale(image, size)
        self._image(icon_scaled_image, (x, y))

        self._rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_tiny, user_input_key, (x + 20, y + h + 4))

    def _text_in_ui(self, font, text, x, y):
        screen_pos = self._translate_ui_position_to_screen((x, y))
        self._text(font, text, screen_pos)

    def _minimap_in_ui(self, position_in_ui, size, player_relative_position):
        pos_in_screen = self._translate_ui_position_to_screen(position_in_ui)
        rect_in_screen = (pos_in_screen[0], pos_in_screen[1], size[0], size[1])
        self._rect_filled((100, 100, 100), rect_in_screen)
        self._rect(COLOR_WHITE, rect_in_screen, 2)
        dot_x = rect_in_screen[0] + player_relative_position[0] * size[0]
        dot_y = rect_in_screen[1] + player_relative_position[1] * size[1]
        dot_w = 4
        self._rect_filled((0, 200, 0), (dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))

    def _tooltip(self, title: str, details: List[str]):
        x_tooltip = 175
        y_tooltip = 280
        w_tooltip = 350
        rect_tooltip = (x_tooltip, y_tooltip, w_tooltip, 170)
        self._rect_filled((100, 100, 130), rect_tooltip)
        self._rect(COLOR_WHITE, rect_tooltip, 3)
        self._text(self.font_large, title, (x_tooltip + 20, y_tooltip + 15), COLOR_WHITE)
        y_separator = y_tooltip + 40
        self._line(COLOR_WHITE, (x_tooltip + 10, y_separator), (x_tooltip + w_tooltip - 10, y_separator), 1)
        for i, detail in enumerate(details):
            self._text(self.font_tiny, detail, (x_tooltip + 20, y_tooltip + 60 + i * 20), COLOR_WHITE)

    def render_world(self, all_entities_to_render, camera_world_area, enemies, is_player_invisible, player_entity,
                     visual_effects, render_hit_and_collision_boxes, player_health, player_max_health, game_world_size):
        self.camera_world_area = camera_world_area

        self.screen.fill(COLOR_BACKGROUND)
        self._world_ground(game_world_size)

        for entity in all_entities_to_render:
            if entity != player_entity:
                self._world_entity(entity)

        if is_player_invisible:
            self._world_rect((200, 100, 250), player_entity.rect(), 1)
        else:
            self._world_entity(player_entity)

        self._stat_bar_for_world_entity(player_entity, 5, -35, player_health, player_max_health, (100, 200, 0))

        if render_hit_and_collision_boxes:
            for entity in all_entities_to_render:
                # hit box
                self._world_rect((250, 250, 250), entity.rect(), 1)
                # collision box
                self._world_rect((50, 250, 0), entity.collision_rect(), 2)

        for enemy in enemies:
            self._stat_bar_for_world_entity(enemy.world_entity, 5, -10, enemy.health, enemy.max_health, COLOR_RED)
        for visual_effect in visual_effects:
            self._visual_effect(visual_effect)

    def render_ui(self, fps_string, is_paused, is_game_over, abilities, ability_cooldowns_remaining,
                  highlighted_ability_action, highlighted_potion_action, message, player_active_buffs,
                  player_health, player_mana, player_max_health, player_max_mana,
                  player_minimap_relative_position, potion_slots, item_slots: Dict[int, ItemType],
                  mouse_screen_position: Tuple[int, int]):

        mouse_ui_position = self._translate_screen_position_to_ui(mouse_screen_position)
        tooltip_title = ""
        tooltip_details = []

        self._rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._rect_filled(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                        self.screen_size[1] - self.camera_size[1]))

        y_1 = 17
        y_2 = y_1 + 20
        y_3 = 105
        y_4 = y_3 + 20

        x_0 = 20
        self._text_in_ui(self.font_large, "HEALTH", x_0, y_1)
        self._stat_bar_in_ui((x_0, y_2 + 2), 100, 28, player_health, player_max_health,
                             COLOR_RED)
        health_text = str(player_health) + "/" + str(player_max_health)
        self._text_in_ui(self.font_large, health_text, x_0 + 20, y_2 + 12)

        self._text_in_ui(self.font_large, "MANA", x_0, y_3)
        self._stat_bar_in_ui((x_0, y_4 + 2), 100, 28, player_mana, player_max_mana, COLOR_BLUE)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._text_in_ui(self.font_large, mana_text, x_0 + 20, y_4 + 12)

        x_1 = 140
        icon_space = 5
        self._text_in_ui(self.font_large, "POTIONS", x_1, y_1)
        for i, slot_number in enumerate(potion_slots):
            x = x_1 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            potion_type = potion_slots[slot_number]
            if is_point_in_rect(mouse_ui_position, (x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                if potion_type:
                    tooltip_title = POTIONS[potion_type].name
            self._potion_icon_in_ui(x, y, UI_ICON_SIZE, slot_number,
                                    potion_type, highlighted_potion_action)

        self._text_in_ui(self.font_large, "SPELLS", x_1, y_3)
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
            self._ability_icon_in_ui(x, y, UI_ICON_SIZE, ability_type,
                                     highlighted_ability_action, ability_cooldowns_remaining)

        x_2 = 338
        self._text_in_ui(self.font_large, "INVENTORY", x_2, y_1)
        for i, item_type in enumerate(item_slots.values()):
            x = x_2 + i * (UI_ICON_SIZE[0] + icon_space)
            y = y_2
            if is_point_in_rect(mouse_ui_position, (x, y, UI_ICON_SIZE[0], UI_ICON_SIZE[1])):
                if item_type:
                    tooltip_title = ITEMS[item_type].name
                    tooltip_details = [ITEMS[item_type].description]
            self._item_icon_in_ui(x, y, UI_ICON_SIZE, item_type)

        x_3 = 465
        self._text_in_ui(self.font_large, "MAP", x_3, y_1)
        self._minimap_in_ui((x_3, y_2), (115, 115), player_minimap_relative_position)

        x_4 = 585
        buff_texts = []
        for active_buff in player_active_buffs:
            buff_type = active_buff.buff_effect.get_buff_type()
            if buff_type in BUFF_TEXTS:
                buff_texts.append(
                    BUFF_TEXTS[buff_type] + " (" + str(int(active_buff.time_until_expiration / 1000)) + ")")
        for i, text in enumerate(buff_texts):
            self._text_in_ui(self.font_small, text, x_4, 15 + i * 25)

        self._rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

        self._rect(COLOR_BLACK, (0, 0, 60, 24), 0)
        self._text(self.font_small, fps_string + " fps", (5, 3))

        if tooltip_title:
            self._tooltip(tooltip_title, tooltip_details)

        self._text(self.font_small, message, (self.ui_screen_area.w / 2 - 80, self.ui_screen_area.y - 30))

        if is_game_over:
            self._text(self.font_huge, "You died!", (self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50))
        elif is_paused:
            self._text(self.font_huge, "PAUSED", (self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50))

    def render_map_editor_ui(self, map_file_entities_by_char: Dict[str, MapFileEntity],
                             placing_map_file_entity: Optional[MapFileEntity]):

        self._rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._rect_filled(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                        self.screen_size[1] - self.camera_size[1]))

        y_1 = 17
        y_2 = y_1 + 20

        x_1 = 155
        icon_space = 5
        self._text_in_ui(self.font_large, "ENTITIES", x_1, y_1)
        i = 0
        for char in map_file_entities_by_char.keys():
            map_file_entity = map_file_entities_by_char[char]
            is_this_entity_being_placed = map_file_entity is placing_map_file_entity
            self._map_editor_icon_in_ui(x_1 + i * (MAP_EDITOR_UI_ICON_SIZE[0] + icon_space), y_2,
                                        MAP_EDITOR_UI_ICON_SIZE, is_this_entity_being_placed, char, map_file_entity)
            i += 1

        self._rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

    def render_map_editor_mouse_rect(self, color: Tuple[int, int, int],
                                     map_editor_mouse_rect: Tuple[int, int, int, int]):
        self._rect(color, map_editor_mouse_rect, 3)

    def render_world_entity_at_position(self, entity: WorldEntity, position: Tuple[int, int]):
        images: Dict[Direction, List[ImageWithRelativePosition]] = self.images_by_sprite[entity.sprite]
        image_with_relative_position = self._get_image_from_direction(images, Direction.DOWN, 0)
        sprite_position = sum_of_vectors(position, image_with_relative_position.position_relative_to_entity)
        self._image(image_with_relative_position.image, sprite_position)
        self._rect((50, 250, 0), (position[0], position[1], entity.w, entity.h), 3)

    @staticmethod
    def update_display():
        pygame.display.update()
