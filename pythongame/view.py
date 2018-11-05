import pygame

from pythongame.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, SpriteInitializer, \
    POTION_ICON_SPRITES, ABILITIES, BUFF_TEXTS
from pythongame.visual_effects import VisualLine, VisualCircle, VisualRect, VisualText

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)
COLOR_HIGHLIGHTED_ICON = (250, 250, 150)
UI_ICON_SIZE = (36, 36)

RENDER_HIT_AND_COLLISION_BOXES = False


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


def load_and_scale_sprite(sprite_initializer):
    image = pygame.image.load(sprite_initializer.image_file_path).convert_alpha()
    return pygame.transform.scale(image, sprite_initializer.scaling_size)


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
        self.images_by_sprite = {sprite: load_and_scale_sprite(ENTITY_SPRITE_INITIALIZERS[sprite])
                                 for sprite in ENTITY_SPRITE_INITIALIZERS}
        self.images_by_ui_sprite = {sprite: load_and_scale_sprite(
            SpriteInitializer(UI_ICON_SPRITE_PATHS[sprite], UI_ICON_SIZE))
            for sprite in UI_ICON_SPRITE_PATHS}

    def _render_entity(self, entity, camera_world_area):
        if entity.sprite is None:
            raise Exception("Entity has no sprite: " + str(entity))
        elif entity.sprite in self.images_by_sprite:
            image = self.images_by_sprite[entity.sprite]
            self._render_entity_sprite(image, entity, camera_world_area)
        else:
            raise Exception("Unhandled sprite: " + str(entity.sprite))

    # TODO: Flesh this out more. Reduce boiler-plate of translating coordinates with the camera
    def _render_rect_in_world(self, camera_world_area, color, rect, line_width=0):
        translated_rect = (rect[0] - camera_world_area.x, rect[1] - camera_world_area.y, rect[2], rect[3])
        self._draw_rect(color, translated_rect, line_width)

    def _draw_rect(self, color, rect, line_width):
        pygame.draw.rect(self.screen, color, rect, line_width)

    def _fill_rect(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)

    def draw_line(self, color, start_position, end_position, line_width):
        pygame.draw.line(self.screen, color, start_position, end_position, line_width)

    def draw_circle(self, color, position, radius, line_width):
        pygame.draw.circle(self.screen, color, position, radius, line_width)

    def _render_entity_sprite(self, image, entity, camera_world_area):
        pos = (entity.x - camera_world_area.x, entity.y - camera_world_area.y)
        self.screen.blit(image, pos)

    def _draw_visual_effect(self, visual_effect, camera_world_area):
        if isinstance(visual_effect, VisualLine):
            self._draw_visual_line(visual_effect, camera_world_area)
        elif isinstance(visual_effect, VisualCircle):
            self._draw_visual_circle(visual_effect, camera_world_area)
        elif isinstance(visual_effect, VisualRect):
            self._draw_visual_rect(visual_effect, camera_world_area)
        elif isinstance(visual_effect, VisualText):
            self._draw_visual_text(visual_effect, camera_world_area)
        else:
            raise Exception("Unhandled visual effect: " + visual_effect)

    def _draw_visual_line(self, line, camera_world_area):
        camera_x = camera_world_area.x
        camera_y = camera_world_area.y
        start_position = line.start_position[0] - camera_x, line.start_position[1] - camera_y
        end_position = line.end_position[0] - camera_x, line.end_position[1] - camera_y
        self.draw_line(line.color, start_position, end_position, line.line_width)

    def _draw_visual_circle(self, visual_circle, camera_world_area):
        position = visual_circle.circle()[0]
        radius = visual_circle.circle()[1]
        translated_position = position[0] - camera_world_area.x, position[1] - camera_world_area.y
        self.draw_circle(visual_circle.color, translated_position, radius, visual_circle.line_width)

    def _draw_visual_rect(self, visual_rect, camera_world_area):
        self._render_rect_in_world(camera_world_area, visual_rect.color, visual_rect.rect(), 1)

    def _draw_visual_text(self, visual_effect, camera_world_area):
        position = visual_effect.position
        translated_position = position[0] - camera_world_area.x, position[1] - camera_world_area.y
        self.screen.blit(self.font_tiny.render(str(visual_effect.text), False, visual_effect.color),
                         translated_position)

    def _render_stat_bar(self, x, y, w, h, stat, max_stat, color, border):
        self._fill_rect((0, 0, 0), (x - 1, y - 1, w + 2, h + 2))
        if border:
            self._draw_rect((250, 250, 250), (x - 2, y - 2, w + 4, h + 4), 2)
        self._fill_rect(color, (x, y, w * stat / max_stat, h))

    def _render_stat_bar_for_entity(self, world_entity, h, stat, max_stat, color, camera_world_area):
        self._render_stat_bar(world_entity.x - camera_world_area.x + 1,
                              world_entity.y - camera_world_area.y - 10,
                              world_entity.w - 2, h, stat, max_stat, color, False)

    def _render_stat_bar_in_ui(self, x_in_ui, y_in_ui, w, h, stat, max_stat, color):
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        self._render_stat_bar(x, y, w, h, stat, max_stat, color, True)

    def _render_ui_potion(self, x_in_ui, y_in_ui, size, potion_number, potion_type, highlighted_potion_action):
        w = size[0]
        h = size[1]
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        self._fill_rect((40, 40, 40), (x, y, w, h))
        if potion_type:
            icon_sprite = POTION_ICON_SPRITES[potion_type]
            self.screen.blit(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._draw_rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted_potion_action == potion_number:
            self._draw_rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self.screen.blit(self.font_tiny.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + h + 4))

    def _render_ui_ability(self, x_in_ui, y_in_ui, size, ability_type, highlighted_ability_action,
                           ability_cooldowns_remaining, max_ability_cooldowns):
        w = size[0]
        h = size[1]
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        ability = ABILITIES[ability_type]
        mana_cost = ability.mana_cost
        icon_sprite = ability.icon_sprite
        self._fill_rect((40, 40, 40), (x, y, w, h))
        self.screen.blit(self.images_by_ui_sprite[icon_sprite], (x, y))
        self._draw_rect(COLOR_WHITE, (x, y, w, h), 2)
        if highlighted_ability_action == ability_type:
            self._draw_rect(COLOR_HIGHLIGHTED_ICON, (x - 1, y - 1, w + 2, h + 2), 3)
        self.screen.blit(self.font_tiny.render(ability.key_string, False, COLOR_WHITE), (x + 8, y + h + 4))
        self.screen.blit(self.font_tiny.render("" + str(mana_cost) + "", False, COLOR_WHITE), (x + 8, y + h + 19))

        if ability_cooldowns_remaining[ability_type] > 0:
            ratio_remaining = ability_cooldowns_remaining[ability_type] / max_ability_cooldowns[ability_type]
            self._fill_rect((100, 30, 30),
                            (x + 2, y + 2 + (h - 4) * (1 - ratio_remaining), w - 4, (h - 4) * ratio_remaining + 2))

    def _render_ui_text(self, font, text, x, y):
        screen_pos = (self.ui_screen_area.x + x, self.ui_screen_area.y + y)
        self._render_text(font, text, screen_pos)

    def _render_text(self, font, text, screen_pos):
        self.screen.blit(font.render(text, False, COLOR_WHITE), screen_pos)

    def _draw_ground(self, camera_world_area):
        line_color = (190, 190, 200)
        grid_width = 25
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        for col in range(num_squares):
            world_x = col * grid_width
            screen_x = world_x - camera_world_area.x
            if 0 < screen_x < self.screen_size[0]:
                self.draw_line(line_color, (screen_x, 0), (screen_x, self.screen_size[1]), 1)
        for row in range(num_squares):
            world_y = row * grid_width
            screen_y = world_y - camera_world_area.y
            if 0 < screen_y < self.screen_size[1]:
                self.draw_line(line_color, (0, screen_y), (self.screen_size[0], screen_y), 1)

    def _render_minimap(self, position_in_ui, size, player_relative_position):
        rect_in_screen = (self.ui_screen_area.x + position_in_ui[0], self.ui_screen_area.y + position_in_ui[1],
                          size[0], size[1])
        self._fill_rect((100, 100, 100), rect_in_screen)
        self._draw_rect(COLOR_WHITE, rect_in_screen, 2)
        dot_x = rect_in_screen[0] + player_relative_position[0] * size[0]
        dot_y = rect_in_screen[1] + player_relative_position[1] * size[1]
        dot_w = 4
        self._fill_rect((0, 200, 0), (dot_x - dot_w / 2, dot_y - dot_w / 2, dot_w, dot_w))

    def render_everything(self, all_entities, player_entity, is_player_invisible, camera_world_area, enemies,
                          player_health, player_max_health, player_mana, player_max_mana, potion_slots,
                          player_active_buffs, visual_effects, fps_string,
                          player_minimap_relative_position, abilities, message, highlighted_potion_action,
                          highlighted_ability_action, is_paused, ability_cooldowns_remaining, max_ability_cooldowns):

        self.screen.fill(COLOR_BACKGROUND)
        self._draw_ground(camera_world_area)

        for entity in all_entities:
            if entity != player_entity:
                self._render_entity(entity, camera_world_area)

        if is_player_invisible:
            self._render_rect_in_world(camera_world_area, (200, 100, 250), player_entity.rect(), 1)
        else:
            self._render_entity(player_entity, camera_world_area)

        if RENDER_HIT_AND_COLLISION_BOXES:
            for entity in all_entities:
                # hit box
                self._render_rect_in_world(camera_world_area, (250, 250, 250), entity.rect(), 1)
                # collision box
                self._render_rect_in_world(camera_world_area, (50, 250, 0), entity.collision_rect(), 2)

        for enemy in enemies:
            self._render_stat_bar_for_entity(enemy.world_entity, 5, enemy.health, enemy.max_health, COLOR_RED,
                                             camera_world_area)

        for visual_effect in visual_effects:
            self._draw_visual_effect(visual_effect, camera_world_area)

        self._draw_rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._fill_rect(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                      self.screen_size[1] - self.camera_size[1]))

        y_1 = 17
        y_2 = y_1 + 20
        y_3 = 105
        y_4 = y_3 + 20

        x_0 = 20
        self._render_ui_text(self.font_large, "HEALTH", x_0, y_1)
        self._render_stat_bar_in_ui(x_0, y_2, 100, 36, player_health, player_max_health,
                                    COLOR_RED)
        health_text = str(player_health) + "/" + str(player_max_health)
        self._render_ui_text(self.font_large, health_text, x_0 + 20, y_2 + 12)

        self._render_ui_text(self.font_large, "MANA", x_0, y_3)
        self._render_stat_bar_in_ui(x_0, y_4, 100, 36, player_mana, player_max_mana, COLOR_BLUE)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._render_ui_text(self.font_large, mana_text, x_0 + 20, y_4 + 12)

        x_1 = 155
        icon_space = 5
        self._render_ui_text(self.font_large, "POTIONS", x_1, y_1)
        self._render_ui_potion(x_1, y_2, UI_ICON_SIZE, 1, potion_slots[1], highlighted_potion_action)
        self._render_ui_potion(x_1 + (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 2, potion_slots[2],
                               highlighted_potion_action)
        self._render_ui_potion(x_1 + 2 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 3, potion_slots[3],
                               highlighted_potion_action)
        self._render_ui_potion(x_1 + 3 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 4, potion_slots[4],
                               highlighted_potion_action)
        self._render_ui_potion(x_1 + 4 * (UI_ICON_SIZE[0] + icon_space), y_2, UI_ICON_SIZE, 5, potion_slots[5],
                               highlighted_potion_action)

        self._render_ui_text(self.font_large, "SPELLS", x_1, y_3)
        for i, ability_type in enumerate(abilities):
            self._render_ui_ability(x_1 + i * (UI_ICON_SIZE[0] + icon_space), y_4, UI_ICON_SIZE, ability_type,
                                    highlighted_ability_action, ability_cooldowns_remaining, max_ability_cooldowns)

        x_2 = 390
        self._render_ui_text(self.font_large, "MAP", x_2, y_1)
        self._render_minimap((x_2, y_2), (125, 125), player_minimap_relative_position)

        buff_texts = []
        for active_buff in player_active_buffs:
            buff_name = BUFF_TEXTS[active_buff.buff_type]
            buff_texts.append(buff_name + " (" + str(int(active_buff.time_until_expiration / 1000)) + ")")
        for i, text in enumerate(buff_texts):
            self._render_ui_text(self.font_small, text, 550, 15 + i * 25)

        self._draw_rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

        self._draw_rect(COLOR_BLACK, (0, 0, 60, 24), 0)
        self._render_text(self.font_small, fps_string + " fps", (5, 3))

        self._render_text(self.font_small, message, (self.ui_screen_area.w / 2 - 80, self.ui_screen_area.y - 30))
        if is_paused:
            self._render_text(self.font_huge, "PAUSED", (self.screen_size[0] / 2 - 110, self.screen_size[1] / 2 - 50))

        pygame.display.update()
