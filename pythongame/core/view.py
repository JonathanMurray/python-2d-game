from typing import Dict, Any

import pygame

from pythongame.core.common import Direction, Sprite
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, SpriteInitializer, \
    POTION_ICON_SPRITES, ABILITIES, BUFF_TEXTS
from pythongame.core.game_state import WorldEntity
from pythongame.core.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
UI_ICON_SIZE = (36, 36)

RENDER_HIT_AND_COLLISION_BOXES = False
RENDER_WORLD_COORDINATES = False


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


def load_and_scale_sprite(sprite_initializer: SpriteInitializer):
    image = pygame.image.load(sprite_initializer.image_file_path).convert_alpha()
    return pygame.transform.scale(image, sprite_initializer.scaling_size)


def load_and_scale_directional_sprites(sprite_initializers_by_dir: Dict[Direction, SpriteInitializer]):
    images = {}
    for direction in sprite_initializers_by_dir:
        sprite_initializer = sprite_initializers_by_dir[direction]
        image = pygame.image.load(sprite_initializer.image_file_path).convert_alpha()
        images[direction] = pygame.transform.scale(image, sprite_initializer.scaling_size)
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
        self.images_by_sprite: Dict[Sprite, Dict[Direction, Any]] = {
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
        self._rect_filled(color, (x, y, w * stat / max_stat, h))

    def _text(self, font, text, screen_pos, color=COLOR_WHITE):
        self.screen.blit(font.render(text, False, color), screen_pos)

    def _image(self, image, position):
        self.screen.blit(image, position)

    # ------------------------------------
    #       DRAWING THE GAME WORLD
    # ------------------------------------

    def _world_ground(self):
        line_color = (190, 190, 200)
        grid_width = 25
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        for col in range(num_squares):
            world_x = col * grid_width
            screen_x = self._translate_world_x_to_screen(world_x)
            if 0 < screen_x < self.screen_size[0]:
                self._line(line_color, (screen_x, 0), (screen_x, self.screen_size[1]), 1)
        for row in range(num_squares):
            world_y = row * grid_width
            screen_y = self._translate_world_y_to_screen(world_y)
            if 0 < screen_y < self.screen_size[1]:
                self._line(line_color, (0, screen_y), (self.screen_size[0], screen_y), 1)

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
            images = self.images_by_sprite[entity.sprite]
            image = self._get_image_from_direction(images, entity.direction)
            pos = self._translate_world_position_to_screen((entity.x, entity.y))
            self._image(image, pos)
        else:
            raise Exception("Unhandled sprite: " + str(entity.sprite))

    def _get_image_from_direction(self, images, direction):
        if direction in images:
            return images[direction]
        else:
            return next(iter(images.values()))

    def _visual_effect(self, visual_effect):
        if isinstance(visual_effect, VisualLine):
            self._visual_line(visual_effect)
        elif isinstance(visual_effect, VisualCircle):
            self._visual_circle(visual_effect)
        elif isinstance(visual_effect, VisualRect):
            self._visual_rect(visual_effect)
        elif isinstance(visual_effect, VisualText):
            self._visual_text(visual_effect)
        else:
            raise Exception("Unhandled visual effect: " + visual_effect)

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
        self._world_rect(visual_rect.color, visual_rect.rect(), 1)

    def _visual_text(self, visual_effect):
        position = visual_effect.position
        translated_position = self._translate_world_position_to_screen(position)
        self._text(self.font_tiny, visual_effect.text, translated_position, visual_effect.color)

    def _stat_bar_for_world_entity(self, world_entity, h, stat, max_stat, color):
        position_on_screen = self._translate_world_position_to_screen((world_entity.x, world_entity.y))
        self._stat_bar(position_on_screen[0] + 1, position_on_screen[1] - 10,
                       world_entity.w - 2, h, stat, max_stat, color, False)

    # ------------------------------------
    #           DRAWING THE UI
    # ------------------------------------

    def _stat_bar_in_ui(self, position_in_ui, w, h, stat, max_stat, color):
        x, y = self._translate_ui_position_to_screen(position_in_ui)
        self._stat_bar(x, y, w, h, stat, max_stat, color, True)

    def _potion_icon_in_ui(self, x_in_ui, y_in_ui, size, potion_number, potion_type, highlighted_potion_action):
        w = size[0]
        h = size[1]
        x, y = self._translate_ui_position_to_screen((x_in_ui, y_in_ui))
        self._rect_filled((40, 40, 40), (x, y, w, h))
        if potion_type:
            icon_sprite = POTION_ICON_SPRITES[potion_type]
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
        mana_cost = ability.mana_cost
        icon_sprite = ability.icon_sprite
        self._rect_filled((40, 40, 40), (x, y, w, h))
        self._image(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted_ability_action == ability_type:
            self._rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self._text(self.font_tiny, ability.key_string, (x + 8, y + h + 4))
        self._text(self.font_tiny, str(mana_cost), (x + 8, y + h + 19))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / ability.cooldown
            cooldown_rect = (x + 2, y + 2 + (h - 4) * (1 - ratio_remaining), w - 4, (h - 4) * ratio_remaining + 2)
            self._rect_filled((100, 30, 30), cooldown_rect)

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

    def render_everything(self, all_entities, player_entity, is_player_invisible, camera_world_area, enemies,
                          player_health, player_max_health, player_mana, player_max_mana, potion_slots,
                          player_active_buffs, visual_effects, fps_string,
                          player_minimap_relative_position, abilities, message, highlighted_potion_action,
                          highlighted_ability_action, is_paused, ability_cooldowns_remaining):

        self.camera_world_area = camera_world_area

        self.screen.fill(COLOR_BACKGROUND)
        self._world_ground()

        for entity in all_entities:
            if entity != player_entity:
                self._world_entity(entity)

        if is_player_invisible:
            self._world_rect((200, 100, 250), player_entity.rect(), 1)
        else:
            self._world_entity(player_entity)

        if RENDER_HIT_AND_COLLISION_BOXES:
            for entity in all_entities:
                # hit box
                self._world_rect((250, 250, 250), entity.rect(), 1)
                # collision box
                self._world_rect((50, 250, 0), entity.collision_rect(), 2)

        for enemy in enemies:
            self._stat_bar_for_world_entity(enemy.world_entity, 5, enemy.health, enemy.max_health, COLOR_RED)

        self._rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._rect_filled(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                        self.screen_size[1] - self.camera_size[1]))

        y_1 = 17
        y_2 = y_1 + 20
        y_3 = 105
        y_4 = y_3 + 20

        x_0 = 20
        self._text_in_ui(self.font_large, "HEALTH", x_0, y_1)
        self._stat_bar_in_ui((x_0, y_2), 100, 36, player_health, player_max_health,
                             COLOR_RED)
        health_text = str(player_health) + "/" + str(player_max_health)
        self._text_in_ui(self.font_large, health_text, x_0 + 20, y_2 + 12)

        self._text_in_ui(self.font_large, "MANA", x_0, y_3)
        self._stat_bar_in_ui((x_0, y_4), 100, 36, player_mana, player_max_mana, COLOR_BLUE)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._text_in_ui(self.font_large, mana_text, x_0 + 20, y_4 + 12)

        x_1 = 155
        icon_space = 5
        self._text_in_ui(self.font_large, "POTIONS", x_1, y_1)
        self._potion_icon_in_ui(x_1, y_2, UI_ICON_SIZE, 1, potion_slots[1], highlighted_potion_action)
        self._potion_icon_in_ui(x_1 + (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 2, potion_slots[2],
                                highlighted_potion_action)
        self._potion_icon_in_ui(x_1 + 2 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 3, potion_slots[3],
                                highlighted_potion_action)
        self._potion_icon_in_ui(x_1 + 3 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 4, potion_slots[4],
                                highlighted_potion_action)
        self._potion_icon_in_ui(x_1 + 4 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 5, potion_slots[5],
                                highlighted_potion_action)

        self._text_in_ui(self.font_large, "SPELLS", x_1, y_3)
        for i, ability_type in enumerate(abilities):
            self._ability_icon_in_ui(x_1 + i * (UI_ICON_SIZE[0] + icon_space), y_4, UI_ICON_SIZE, ability_type,
                                     highlighted_ability_action, ability_cooldowns_remaining)

        x_2 = 390
        self._text_in_ui(self.font_large, "MAP", x_2, y_1)
        self._minimap_in_ui((x_2, y_2), (125, 125), player_minimap_relative_position)

        buff_texts = []
        for active_buff in player_active_buffs:
            buff_name = BUFF_TEXTS[active_buff.buff_type]
            buff_texts.append(buff_name + " (" + str(int(active_buff.time_until_expiration / 1000)) + ")")
        for i, text in enumerate(buff_texts):
            self._text_in_ui(self.font_small, text, 550, 15 + i * 25)

        self._rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

        self._rect(COLOR_BLACK, (0, 0, 60, 24), 0)
        self._text(self.font_small, fps_string + " fps", (5, 3))

        self._text(self.font_small, message, (self.ui_screen_area.w / 2 - 80, self.ui_screen_area.y - 30))
        if is_paused:
            self._text(self.font_huge, "PAUSED", (self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50))

        for visual_effect in visual_effects:
            self._visual_effect(visual_effect)

        pygame.display.update()
