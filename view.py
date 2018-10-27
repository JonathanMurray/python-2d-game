import pygame

from common import *

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)
UI_POTION_SIZE = (27, 27)


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


class SpriteInitializer:
    def __init__(self, image_file_path, scaling_size):
        self.image_file_path = image_file_path
        self.scaling_size = scaling_size


def load_and_scale_sprite(sprite_initializer):
    image = pygame.image.load(sprite_initializer.image_file_path).convert_alpha()
    return pygame.transform.scale(image, sprite_initializer.scaling_size)


class View:

    def __init__(self, screen, ui_screen_area, camera_size, screen_size, sprite_initializers_by_sprite):
        self.screen = screen
        self.ui_screen_area = ui_screen_area
        self.camera_size = camera_size
        self.screen_size = screen_size
        self.font_large = pygame.font.SysFont('Arial', 30)
        self.font_small = pygame.font.Font(None, 25)
        self.images_by_sprite = {sprite: load_and_scale_sprite(sprite_initializers_by_sprite[sprite])
                                 for sprite in sprite_initializers_by_sprite}
        # TODO: Handle potion sprites in a more dynamic way

        self.health_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/ui_health_potion.png", UI_POTION_SIZE))
        self.mana_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/ui_mana_potion.png", UI_POTION_SIZE))
        self.speed_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/white_potion.gif", UI_POTION_SIZE))

    def _render_entity(self, entity, camera_world_area):
        rect = (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h)
        if entity.sprite is None:
            pygame.draw.rect(self.screen, entity.color, rect)
        elif entity.sprite in self.images_by_sprite:
            image = self.images_by_sprite[entity.sprite]
            self._render_entity_sprite(image, entity, camera_world_area)
        else:
            raise Exception("Unhandled sprite: " + str(entity.sprite))

    def _render_entity_sprite(self, image, entity, camera_world_area):
        pos = (entity.x - camera_world_area.x, entity.y - camera_world_area.y)
        self.screen.blit(image, pos)

    def _render_stat_bar(self, x, y, w, h, stat, max_stat, color):
        pygame.draw.rect(self.screen, COLOR_WHITE, (x - 2, y - 2, w + 3, h + 3), 2)
        pygame.draw.rect(self.screen, color, (x, y, w * stat / max_stat, h))

    def _render_stat_bar_for_entity(self, world_entity, h, stat, max_stat, color, camera_world_area):
        self._render_stat_bar(world_entity.x - camera_world_area.x + 1,
                              world_entity.y - camera_world_area.y - 10,
                              world_entity.w - 2, h, stat, max_stat, color)

    def _render_stat_bar_in_ui(self, x_in_ui, y_in_ui, w, h, stat, max_stat, color):
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        self._render_stat_bar(x, y, w, h, stat, max_stat, color)

    def _render_ui_potion(self, x_in_ui, y_in_ui, size, potion_number, potion_type):
        w = size[0]
        h = size[1]
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h), 3)
        if potion_type == PotionType.HEALTH:
            self.screen.blit(self.health_potion_image, (x, y))
        elif potion_type == PotionType.MANA:
            self.screen.blit(self.mana_potion_image, (x, y))
        elif potion_type == PotionType.SPEED:
            self.screen.blit(self.speed_potion_image, (x, y))
        else:
            self.screen.blit(self.font_small.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + 5))

    def _render_ui_text(self, font, text, x, y):
        self.screen.blit(font.render(text, False, COLOR_WHITE), (self.ui_screen_area.x + x, self.ui_screen_area.y + y))

    def _render_rect(self, color, rect, width):
        pygame.draw.rect(self.screen, color, rect, width)

    def _render_rect_filled(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)

    def _draw_ground(self, camera_world_area):
        line_color = (190, 190, 200)
        grid_width = 25
        # TODO num squares should depend on map size. Ideally this dumb looping logic should change.
        num_squares = 200
        for col in range(num_squares):
            world_x = col * grid_width
            screen_x = world_x - camera_world_area.x
            if 0 < screen_x < self.screen_size[0]:
                pygame.draw.line(self.screen, line_color, (screen_x, 0), (screen_x, self.screen_size[1]))
        for row in range(num_squares):
            world_y = row * grid_width
            screen_y = world_y - camera_world_area.y
            if 0 < screen_y < self.screen_size[1]:
                pygame.draw.line(self.screen, line_color, (0, screen_y), (self.screen_size[0], screen_y))

    def render_everything(self, all_entities, camera_world_area, enemies, player_health,
                          player_max_health, player_mana, player_max_mana, potion_slots, has_effect_healing_over_time,
                          time_until_effect_expires, has_effect_poison, time_until_poison_expires,
                          has_effect_speed, time_until_speed_expires):
        self.screen.fill(COLOR_BACKGROUND)
        self._draw_ground(camera_world_area)

        for entity in all_entities:
            self._render_entity(entity, camera_world_area)

        for enemy in enemies:
            self._render_stat_bar_for_entity(enemy.world_entity, 5, enemy.health, enemy.max_health, COLOR_RED,
                                             camera_world_area)

        self._render_rect(COLOR_BLACK, (0, 0, self.camera_size[0], self.camera_size[1]), 3)
        self._render_rect_filled(COLOR_BLACK, (0, self.camera_size[1], self.screen_size[0],
                                               self.screen_size[1] - self.camera_size[1]))

        self._render_ui_text(self.font_large, "Health", 10, 10)
        self._render_stat_bar_in_ui(10, 40, 100, 25, player_health, player_max_health,
                                    COLOR_RED)
        health_text = str(player_health) + "/" + str(player_max_health)
        self._render_ui_text(self.font_large, health_text, 30, 43)

        self._render_ui_text(self.font_large, "Mana", 130, 10)
        self._render_stat_bar_in_ui(130, 40, 100, 25, player_mana, player_max_mana, COLOR_BLUE)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._render_ui_text(self.font_large, mana_text, 150, 43)

        self._render_ui_text(self.font_large, "Potions", 250, 10)
        self._render_ui_potion(250, 39, UI_POTION_SIZE, 1, potion_type=potion_slots[1])
        self._render_ui_potion(280, 39, UI_POTION_SIZE, 2, potion_type=potion_slots[2])
        self._render_ui_potion(310, 39, UI_POTION_SIZE, 3, potion_type=potion_slots[3])
        self._render_ui_potion(340, 39, UI_POTION_SIZE, 4, potion_type=potion_slots[4])
        self._render_ui_potion(370, 39, UI_POTION_SIZE, 5, potion_type=potion_slots[5])

        ui_text = "Abilities: Q(" + str(ability_mana_costs[AbilityType.ATTACK]) + ") " + \
                  "W(" + str(ability_mana_costs[AbilityType.HEAL]) + ") " + \
                  "E(" + str(ability_mana_costs[AbilityType.AOE_ATTACK]) + ")"
        self._render_ui_text(self.font_small, ui_text, 20, 75)

        # TODO Generalise rendering of effects that can expire
        effect_texts = []
        if has_effect_healing_over_time:
            effect_texts.append("Healing over time (" + str(int(time_until_effect_expires/1000)) + ")")
        if has_effect_poison:
            effect_texts.append("Poison (" + str(int(time_until_poison_expires/1000)) + ")")
        if has_effect_speed:
            effect_texts.append("Speed (" + str(int(time_until_speed_expires/1000)) + ")")
        for i, text in enumerate(effect_texts):
            self._render_ui_text(self.font_small, text, 450, 25 + i * 35)

        self._render_rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)
        pygame.display.update()
