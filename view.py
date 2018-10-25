import pygame

from common import PotionType

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


class View:

    def __init__(self, screen, ui_screen_area, camera_size, screen_size):
        self.screen = screen
        self.ui_screen_area = ui_screen_area
        self.camera_size = camera_size
        self.screen_size = screen_size
        self.font_large = pygame.font.SysFont('Arial', 30)
        self.font_small = pygame.font.Font(None, 25)

    def _render_entity(self, entity, camera_world_area):
        rect = (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h)
        pygame.draw.rect(self.screen, entity.color, rect)

    def _render_circle(self, entity, camera_world_area):
        rect = (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h)
        pygame.draw.ellipse(self.screen, COLOR_BLUE, rect)

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

    def _render_ui_potion(self, x_in_ui, y_in_ui, w, h, potion_number, potion_type):
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, w, h), 3)
        if potion_type == PotionType.HEALTH:
            pygame.draw.rect(self.screen, (250, 50, 50), (x, y, w, h))
        if potion_type == PotionType.MANA:
            pygame.draw.rect(self.screen, (50, 50, 250), (x, y, w, h))
        self.screen.blit(self.font_large.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + 5))

    def _render_ui_text(self, font, text, x, y):
        self.screen.blit(font.render(text, False, COLOR_WHITE), (self.ui_screen_area.x + x, self.ui_screen_area.y + y))

    def _render_rect(self, color, rect, width):
        pygame.draw.rect(self.screen, color, rect, width)

    def _render_rect_filled(self, color, rect):
        pygame.draw.rect(self.screen, color, rect)

    def render_everything(self, all_entities, camera_world_area, player_entity, enemies, player_health,
                          player_max_health, player_mana, player_max_mana, potion_slots, heal_ability_mana_cost,
                          attack_ability_mana_cost):
        self.screen.fill(COLOR_BACKGROUND)
        for entity in all_entities:
            self._render_entity(entity, camera_world_area)
        self._render_circle(player_entity, camera_world_area)

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
        self._render_ui_potion(250, 39, 27, 27, 1, potion_type=potion_slots[1])
        self._render_ui_potion(280, 39, 27, 27, 2, potion_type=potion_slots[2])
        self._render_ui_potion(310, 39, 27, 27, 3, potion_type=potion_slots[3])
        self._render_ui_potion(340, 39, 27, 27, 4, potion_type=potion_slots[4])
        self._render_ui_potion(370, 39, 27, 27, 5, potion_type=potion_slots[5])

        ui_text = "Abilities: Q(" + str(attack_ability_mana_cost) + ") " + \
                  "W(" + str(heal_ability_mana_cost) + ")"
        self._render_ui_text(self.font_small, ui_text, 20, 75)

        self._render_rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)
        pygame.display.update()
