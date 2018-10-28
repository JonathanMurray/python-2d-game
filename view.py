import pygame

from common import *

COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)
UI_POTION_SIZE = (27, 27)
UI_ABILITY_SIZE = (27, 27)


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
        self.font_large = pygame.font.SysFont('Arial', 22)
        self.font_small = pygame.font.Font(None, 25)
        self.font_tiny = pygame.font.Font(None, 19)
        self.images_by_sprite = {sprite: load_and_scale_sprite(sprite_initializers_by_sprite[sprite])
                                 for sprite in sprite_initializers_by_sprite}

        # TODO: Handle icon sprites in a more dynamic way
        self.health_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/ui_health_potion.png", UI_POTION_SIZE))
        self.mana_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/ui_mana_potion.png", UI_POTION_SIZE))
        self.speed_potion_image = load_and_scale_sprite(
            SpriteInitializer("resources/white_potion.gif", UI_POTION_SIZE))
        self.attack_ability_image = load_and_scale_sprite(
            SpriteInitializer("resources/fireball.png", UI_ABILITY_SIZE))
        self.heal_ability_image = load_and_scale_sprite(
            SpriteInitializer("resources/heal_ability.png", UI_ABILITY_SIZE))
        self.aoe_ability_image = load_and_scale_sprite(
            SpriteInitializer("resources/whirlwind.png", UI_ABILITY_SIZE))

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
        if potion_type == PotionType.HEALTH:
            self.screen.blit(self.health_potion_image, (x, y))
        elif potion_type == PotionType.MANA:
            self.screen.blit(self.mana_potion_image, (x, y))
        elif potion_type == PotionType.SPEED:
            self.screen.blit(self.speed_potion_image, (x, y))
        pygame.draw.rect(self.screen, COLOR_WHITE, (x, y, w, h), 2)
        self.screen.blit(self.font_tiny.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + h + 4))

    def _render_ui_ability(self, x_in_ui, y_in_ui, size, key, ability_type):
        w = size[0]
        h = size[1]
        x = self.ui_screen_area.x + x_in_ui
        y = self.ui_screen_area.y + y_in_ui
        mana_cost = ability_mana_costs[ability_type]
        if ability_type == AbilityType.ATTACK:
            self.screen.blit(self.attack_ability_image, (x, y))
        elif ability_type == AbilityType.HEAL:
            self.screen.blit(self.heal_ability_image, (x, y))
        elif ability_type == AbilityType.AOE_ATTACK:
            self.screen.blit(self.aoe_ability_image, (x, y))
        pygame.draw.rect(self.screen, COLOR_WHITE, (x, y, w, h), 2)
        self.screen.blit(self.font_tiny.render(key, False, COLOR_WHITE), (x + 8, y + h + 4))
        self.screen.blit(self.font_tiny.render("" + str(mana_cost) + "", False, COLOR_WHITE), (x + 8, y + h + 19))

    def _render_ui_text(self, font, text, x, y):
        screen_pos = (self.ui_screen_area.x + x, self.ui_screen_area.y + y)
        self._render_text(font, text, screen_pos)

    def _render_text(self, font, text, screen_pos):
        self.screen.blit(font.render(text, False, COLOR_WHITE), screen_pos)

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
                          player_max_health, player_mana, player_max_mana, potion_slots, buffs, fps_string):
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

        y_1 = 17
        y_2 = 40
        y_3 = 107
        y_4 = 130

        x_0 = 20
        self._render_ui_text(self.font_large, "HEALTH", x_0, y_1)
        self._render_stat_bar_in_ui(x_0, y_2 + 2, 100, 25, player_health, player_max_health,
                                    COLOR_RED)
        health_text = str(player_health) + "/" + str(player_max_health)
        self._render_ui_text(self.font_large, health_text, x_0 + 20, y_2 + 8)

        self._render_ui_text(self.font_large, "MANA", x_0, y_3)
        self._render_stat_bar_in_ui(x_0, y_4 + 2, 100, 25, player_mana, player_max_mana, COLOR_BLUE)
        mana_text = str(player_mana) + "/" + str(player_max_mana)
        self._render_ui_text(self.font_large, mana_text, x_0 + 20, y_4 + 8)

        x_1 = 170
        self._render_ui_text(self.font_large, "POTIONS", x_1, y_1)
        self._render_ui_potion(x_1, y_2, UI_POTION_SIZE, 1, potion_type=potion_slots[1])
        self._render_ui_potion(x_1 + 30, y_2, UI_POTION_SIZE, 2, potion_type=potion_slots[2])
        self._render_ui_potion(x_1 + 60, y_2, UI_POTION_SIZE, 3, potion_type=potion_slots[3])
        self._render_ui_potion(x_1 + 90, y_2, UI_POTION_SIZE, 4, potion_type=potion_slots[4])
        self._render_ui_potion(x_1 + 120, y_2, UI_POTION_SIZE, 5, potion_type=potion_slots[5])

        self._render_ui_text(self.font_large, "SPELLS", x_1, y_3)
        self._render_ui_ability(x_1, y_4, UI_ABILITY_SIZE, "Q", AbilityType.ATTACK)
        self._render_ui_ability(x_1 + 30, y_4, UI_ABILITY_SIZE, "W", AbilityType.HEAL)
        self._render_ui_ability(x_1 + 60, y_4, UI_ABILITY_SIZE, "E", AbilityType.AOE_ATTACK)

        buff_texts = []
        for buff in buffs:
            if buff.buff_type == BuffType.DAMAGE_OVER_TIME:
                buff_name = "Poison"
            elif buff.buff_type == BuffType.INCREASED_MOVE_SPEED:
                buff_name = "Speed"
            elif buff.buff_type == BuffType.HEALING_OVER_TIME:
                buff_name = "Healing"
            else:
                raise Exception("Unhandled buff type: " + buff.buff_type)
            buff_texts.append(buff_name + "(" + str(int(buff.time_until_expiration/1000)) + ")")
        for i, text in enumerate(buff_texts):
            self._render_ui_text(self.font_small, text, 550, 15 + i * 25)

        self._render_rect(COLOR_WHITE, self.ui_screen_area.rect(), 1)

        self._render_text(self.font_small, fps_string + " FPS", (10, 10))

        pygame.display.update()
