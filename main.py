#!/usr/bin/env python3

import math
import pygame
import sys
from enum import Enum
import random


class WorldArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class WorldEntity:
    def __init__(self, pos, size, color, direction=Direction.LEFT, speed=0, max_speed=0):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]
        self.color = color
        self.direction = direction
        self.speed = speed
        self.max_speed = max_speed

    def set_moving_in_dir(self, direction):
        self.direction = direction
        self.speed = self.max_speed

    def set_not_moving(self):
        self.speed = 0

    def update_position_according_to_dir_and_speed(self):
        if self.direction == Direction.LEFT:
            self.x -= self.speed
        elif self.direction == Direction.RIGHT:
            self.x += self.speed
        elif self.direction == Direction.UP:
            self.y -= self.speed
        elif self.direction == Direction.DOWN:
            self.y += self.speed

    def get_center_x(self):
        return self.x + self.w / 2

    def get_center_y(self):
        return self.y + self.h / 2


class Enemy:
    def __init__(self, world_entity, health, max_health):
        self.world_entity = world_entity
        self.health = health
        self.max_health = max_health
        self.movement_error_chance = 0.2

    def run_ai_with_target(self, target_entity):
        dx = target_entity.x - self.world_entity.x
        dy = target_entity.y - self.world_entity.y
        if abs(dx) > abs(dy):
            if dx > 0:
                direction = Direction.RIGHT
            else:
                direction = Direction.LEFT
        else:
            if dy < 0:
                direction = Direction.UP
            else:
                direction = Direction.DOWN
        if random.random() < self.movement_error_chance:
            direction = random.choice(get_perpendicular_directions(direction))
        self.world_entity.set_moving_in_dir(direction)


def get_perpendicular_directions(direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


class PlayerStats:
    def __init__(self, health, max_health, mana, max_mana):
        self.health = health
        self.max_health = max_health
        self.mana = mana
        self._mana_float = mana
        self.max_mana = max_mana

    def gain_health(self, amount):
        self.health = min(self.health + amount, self.max_health)

    def lose_health(self, amount):
        self.health -= amount

    def gain_mana(self, amount):
        self._mana_float = min(self._mana_float + amount, self.max_mana)
        self.mana = int(math.floor(self._mana_float))

    def lose_mana(self, amount):
        self._mana_float -= amount
        self.mana = int(math.floor(self._mana_float))


class GameState:
    def __init__(self, player_pos, potion_positions, enemy_positions):
        self.camera_world_area = WorldArea((0, 0), CAMERA_SIZE)
        self.player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, PLAYER_ENTITY_COLOR, Direction.RIGHT, 0,
                                         PLAYER_ENTITY_SPEED)
        self.projectile_entities = []
        self.potion_entities = [WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_COLOR) for pos in potion_positions]
        self.enemies = [Enemy(WorldEntity(pos, ENEMY_SIZE, ENEMY_COLOR, Direction.LEFT, ENEMY_SPEED, ENEMY_SPEED), 2, 2)
                        for pos in enemy_positions]
        self.player_stats = PlayerStats(3, 20, 50, 100)
        self.health_potion_slots = {
            1: True,
            2: False,
            3: True,
            4: True,
            5: True
        }

    def remove_entities(self, entities_to_remove):
        self.projectile_entities = [p for p in self.projectile_entities if p not in entities_to_remove]
        self.potion_entities = [p for p in self.potion_entities if p not in entities_to_remove]
        self.enemies = [e for e in self.enemies if e not in entities_to_remove]

    def try_use_health_potion(self, number):
        if self.health_potion_slots[number]:
            self.health_potion_slots[number] = False
            self.player_stats.gain_health(10)

    # Returns whether or not potion was picked up (not picked up if no space for it)
    def try_pick_up_potion(self):
        empty_slots = [slot for slot in self.health_potion_slots if not self.health_potion_slots[slot]]
        if len(empty_slots) > 0:
            slot = empty_slots[0]
            self.health_potion_slots[slot] = True
            return True
        else:
            return False


def render_entity(entity):
    rect = (entity.x - game_state.camera_world_area.x, entity.y - game_state.camera_world_area.y, entity.w, entity.h)
    pygame.draw.rect(SCREEN, entity.color, rect)


def render_circle(entity):
    rect = (entity.x - game_state.camera_world_area.x, entity.y - game_state.camera_world_area.y, entity.w, entity.h)
    pygame.draw.ellipse(SCREEN, COLOR_BLUE, rect)


def _render_stat_bar(x, y, w, h, stat, max_stat, color):
    pygame.draw.rect(SCREEN, COLOR_WHITE, (x - 2, y - 2, w + 3, h + 3), 2)
    pygame.draw.rect(SCREEN, color, (x, y, w * stat / max_stat, h))


def render_stat_bar_for_entity(world_entity, h, stat, max_stat, color):
    _render_stat_bar(world_entity.x - game_state.camera_world_area.x + 1,
                     world_entity.y - game_state.camera_world_area.y - 10,
                     world_entity.w - 2, h, stat, max_stat, color)


def render_stat_bar_in_ui(x_in_ui, y_in_ui, w, h, stat, max_stat, color):
    x = UI_SCREEN_AREA.x + x_in_ui
    y = UI_SCREEN_AREA.y + y_in_ui
    _render_stat_bar(x, y, w, h, stat, max_stat, color)


def render_ui_potion(x_in_ui, y_in_ui, w, h, potion_number):
    x = UI_SCREEN_AREA.x + x_in_ui
    y = UI_SCREEN_AREA.y + y_in_ui
    pygame.draw.rect(SCREEN, (100, 100, 100), (x, y, w, h), 3)
    if game_state.health_potion_slots[potion_number]:
        pygame.draw.rect(SCREEN, (250, 50, 50), (x, y, w, h))
    SCREEN.blit(FONT_LARGE.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + 5))


def render_ui_text(font, text, x, y):
    SCREEN.blit(font.render(text, False, COLOR_WHITE), (UI_SCREEN_AREA.x + x, UI_SCREEN_AREA.y + y))


def ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)


def boxes_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
           and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)


def update_world_entity_position_within_game_boundary(world_entity):
    world_entity.update_position_according_to_dir_and_speed()
    world_entity.x = min(max(world_entity.x, 0), GAME_WORLD_SIZE[0] - world_entity.w)
    world_entity.y = min(max(world_entity.y, 0), GAME_WORLD_SIZE[1] - world_entity.h)


def init_game_state_from_file():
    enemy_positions = []
    potion_positions = []
    player_pos = (0, 0)
    with open("map.txt") as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (GAME_WORLD_SIZE[0] * col_index / 100, GAME_WORLD_SIZE[1] * row_index / 50)
                if char == 'P':
                    player_pos = game_world_pos
                if char == 'E':
                    enemy_positions.append(game_world_pos)
                if char == 'H':
                    potion_positions.append(game_world_pos)
                col_index += 1
            row_index += 1
    return GameState(player_pos, potion_positions, enemy_positions)


COLOR_ATTACK_PROJECTILE = (200, 5, 200)
COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)

SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 500)
UI_SCREEN_AREA = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
GAME_WORLD_SIZE = (1000, 1000)
ENTIRE_WORLD_AREA = WorldArea((0, 0), GAME_WORLD_SIZE)

POTION_ENTITY_SIZE = (30, 30)
POTION_ENTITY_COLOR = (50, 200, 50)
ENEMY_SIZE = (30, 30)
ENEMY_COLOR = COLOR_RED
ENEMY_SPEED = 0.4
PLAYER_MANA_REGEN = 0.03
PLAYER_ENTITY_SIZE = (50, 50)
PLAYER_ENTITY_COLOR = (250, 250, 250)
PLAYER_ENTITY_SPEED = 2
ATTACK_PROJECTILE_SIZE = (35, 35)
ATTACK_PROJECTILE_SPEED = 4
HEAL_ABILITY_MANA_COST = 10
HEAL_ABILITY_AMOUNT = 10
ATTACK_ABILITY_MANA_COST = 5
PYGAME_MOVEMENT_KEYS = [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN]
DIRECTION_BY_PYGAME_MOVEMENT_KEY = {
    pygame.K_LEFT: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT,
    pygame.K_UP: Direction.UP,
    pygame.K_DOWN: Direction.DOWN
}

game_state = init_game_state_from_file()
pygame.init()
pygame.font.init()
FONT_LARGE = pygame.font.SysFont('Arial', 30)
FONT_SMALL = pygame.font.Font(None, 25)
SCREEN = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
ticks_since_ai_ran = 0
AI_RUN_INTERVAL = 750

movement_keys_down = []

while True:

    # ------------------------------------
    #         HANDLE EVENTS
    # ------------------------------------

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key in PYGAME_MOVEMENT_KEYS:
                if event.key in movement_keys_down:
                    movement_keys_down.remove(event.key)
                movement_keys_down.append(event.key)
            elif event.key == pygame.K_a:
                if game_state.player_stats.mana >= HEAL_ABILITY_MANA_COST:
                    game_state.player_stats.lose_mana(HEAL_ABILITY_MANA_COST)
                    game_state.player_stats.gain_health(HEAL_ABILITY_AMOUNT)
            elif event.key == pygame.K_f:
                if game_state.player_stats.mana >= ATTACK_ABILITY_MANA_COST:
                    game_state.player_stats.lose_mana(ATTACK_ABILITY_MANA_COST)
                    proj_pos = (game_state.player_entity.get_center_x() - ATTACK_PROJECTILE_SIZE[0] / 2,
                                game_state.player_entity.get_center_y() - ATTACK_PROJECTILE_SIZE[1] / 2)
                    game_state.projectile_entities.append(WorldEntity(
                        proj_pos, ATTACK_PROJECTILE_SIZE, COLOR_ATTACK_PROJECTILE, game_state.player_entity.direction,
                        ATTACK_PROJECTILE_SPEED, ATTACK_PROJECTILE_SPEED))
            elif event.key == pygame.K_1:
                game_state.try_use_health_potion(1)
            elif event.key == pygame.K_2:
                game_state.try_use_health_potion(2)
            elif event.key == pygame.K_3:
                game_state.try_use_health_potion(3)
            elif event.key == pygame.K_4:
                game_state.try_use_health_potion(4)
            elif event.key == pygame.K_5:
                game_state.try_use_health_potion(5)
        if event.type == pygame.KEYUP:
            if event.key in PYGAME_MOVEMENT_KEYS:
                movement_keys_down.remove(event.key)
        if movement_keys_down:
            last_pressed_movement_key = movement_keys_down[-1]
            game_state.player_entity.set_moving_in_dir(DIRECTION_BY_PYGAME_MOVEMENT_KEY[last_pressed_movement_key])
        else:
            game_state.player_entity.set_not_moving()

    # ------------------------------------
    #         RUN ENEMY AI
    # ------------------------------------

    clock.tick()
    ticks_since_ai_ran += clock.get_time()
    if ticks_since_ai_ran > AI_RUN_INTERVAL:
        ticks_since_ai_ran = 0
        for e in game_state.enemies:
            e.run_ai_with_target(game_state.player_entity)

    # ------------------------------------
    #         UPDATE MOVING ENTITIES
    # ------------------------------------

    for e in game_state.enemies:
        # Enemies shouldn't move towards player when they are out of sight
        if boxes_intersect(e.world_entity, game_state.camera_world_area):
            update_world_entity_position_within_game_boundary(e.world_entity)
    update_world_entity_position_within_game_boundary(game_state.player_entity)
    for projectile in game_state.projectile_entities:
        projectile.update_position_according_to_dir_and_speed()

    # ------------------------------------
    #         HANDLE COLLISIONS
    # ------------------------------------

    entities_to_remove = []
    for projectile in game_state.projectile_entities:
        if not boxes_intersect(projectile, ENTIRE_WORLD_AREA):
            entities_to_remove.append(projectile)
    for potion in game_state.potion_entities:
        if boxes_intersect(game_state.player_entity, potion):
            did_pick_up = game_state.try_pick_up_potion()
            if did_pick_up:
                entities_to_remove.append(potion)
    for enemy in game_state.enemies:
        if boxes_intersect(game_state.player_entity, enemy.world_entity):
            entities_to_remove.append(enemy)
            game_state.player_stats.lose_health(2)
        for projectile in game_state.projectile_entities:
            if boxes_intersect(enemy.world_entity, projectile):
                enemy.health -= 1
                if enemy.health <= 0:
                    entities_to_remove.append(enemy)
                entities_to_remove.append(projectile)
    game_state.remove_entities(entities_to_remove)

    # ------------------------------------
    #         REGEN MANA
    # ------------------------------------

    game_state.player_stats.gain_mana(PLAYER_MANA_REGEN)

    # ------------------------------------
    #         UPDATE CAMERA POSITION
    # ------------------------------------

    game_state.camera_world_area.x = min(max(game_state.player_entity.x - CAMERA_SIZE[0] / 2, 0),
                                         GAME_WORLD_SIZE[0] - CAMERA_SIZE[0])
    game_state.camera_world_area.y = min(max(game_state.player_entity.y - CAMERA_SIZE[1] / 2, 0),
                                         GAME_WORLD_SIZE[1] - CAMERA_SIZE[1])

    # ------------------------------------
    #         RENDER EVERYTHING
    # ------------------------------------

    SCREEN.fill(COLOR_BACKGROUND)
    for entity in game_state.potion_entities + [e.world_entity for e in game_state.enemies] \
                  + [p for p in game_state.projectile_entities]:
        render_entity(entity)

    render_entity(game_state.player_entity)
    render_circle(game_state.player_entity)

    for enemy in game_state.enemies:
        render_stat_bar_for_entity(enemy.world_entity, 5, enemy.health, enemy.max_health, COLOR_RED)

    pygame.draw.rect(SCREEN, COLOR_BLACK, (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
    pygame.draw.rect(SCREEN, COLOR_BLACK, (0, CAMERA_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))

    render_ui_text(FONT_LARGE, "Health", 10, 10)
    render_stat_bar_in_ui(10, 40, 100, 25, game_state.player_stats.health, game_state.player_stats.max_health,
                          COLOR_RED)
    health_text = str(game_state.player_stats.health) + "/" + str(game_state.player_stats.max_health)
    render_ui_text(FONT_LARGE, health_text, 30, 43)

    render_ui_text(FONT_LARGE, "Mana", 130, 10)
    render_stat_bar_in_ui(130, 40, 100, 25, game_state.player_stats.mana, game_state.player_stats.max_mana, COLOR_BLUE)
    mana_text = str(game_state.player_stats.mana) + "/" + str(game_state.player_stats.max_mana)
    render_ui_text(FONT_LARGE, mana_text, 150, 43)

    render_ui_text(FONT_LARGE, "Potions", 250, 10)
    render_ui_potion(250, 39, 27, 27, 1)
    render_ui_potion(280, 39, 27, 27, 2)
    render_ui_potion(310, 39, 27, 27, 3)
    render_ui_potion(340, 39, 27, 27, 4)
    render_ui_potion(370, 39, 27, 27, 5)

    ui_text = "['A' to heal (" + str(HEAL_ABILITY_MANA_COST) + ")] " + \
              "['F' to attack (" + str(ATTACK_ABILITY_MANA_COST) + ")]"
    render_ui_text(FONT_SMALL, ui_text, 20, 75)

    pygame.draw.rect(SCREEN, COLOR_WHITE, UI_SCREEN_AREA.rect(), 1)
    pygame.display.update()
