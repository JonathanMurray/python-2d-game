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


def render_entity(screen, entity, camera_world_area):
    pygame.draw.rect(screen, entity.color,
                     (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h))


def render_circle(screen, entity, camera_world_area):
    pygame.draw.ellipse(screen, COLOR_BLUE,
                        (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h))


def ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)


def boxes_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
           and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)


def render_stat_bar(screen, x, y, w, h, stat, max_stat, color):
    pygame.draw.rect(screen, COLOR_WHITE, (x - 2, y - 2, w + 3, h + 3), 2)
    pygame.draw.rect(screen, color, (x, y, w * stat / max_stat, h))


def update_world_entity_position(world_entity):
    if world_entity.direction == Direction.LEFT:
        world_entity.x -= world_entity.speed
    elif world_entity.direction == Direction.RIGHT:
        world_entity.x += world_entity.speed
    elif world_entity.direction == Direction.UP:
        world_entity.y -= world_entity.speed
    elif world_entity.direction == Direction.DOWN:
        world_entity.y += world_entity.speed


def update_world_entity_position_within_game_boundary(world_entity):
    update_world_entity_position(world_entity)
    world_entity.x = min(max(world_entity.x, 0), GAME_WORLD_SIZE[0] - world_entity.w)
    world_entity.y = min(max(world_entity.y, 0), GAME_WORLD_SIZE[1] - world_entity.h)


def try_use_health_potion(number):
    if health_potions[number]:
        health_potions[number] = False
        player_stats.gain_health(10)


def render_ui_potion(screen, x, y, w, h, potion_number):
    pygame.draw.rect(screen, (100, 100, 100), (x, y, w, h), 3)
    if health_potions[potion_number]:
        pygame.draw.rect(screen, (250, 50, 50), (x, y, w, h))
    screen.blit(FONT_LARGE.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + 5))


# Returns whether or not potion was picked up (not picked up if no space for it)
def try_pick_up_potion():
    empty_slots = [slot for slot in health_potions if not health_potions[slot]]
    if len(empty_slots) > 0:
        slot = empty_slots[0]
        health_potions[slot] = True
        return True
    else:
        return False


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

# ------------------------------------
#         READ MAP FROM TEXT FILE
# ------------------------------------

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

pygame.init()
pygame.font.init()
FONT_LARGE = pygame.font.SysFont('Arial', 30)
FONT_SMALL = pygame.font.Font(None, 25)
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()

camera_world_area = WorldArea((0, 0), CAMERA_SIZE)
player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, PLAYER_ENTITY_COLOR, Direction.RIGHT, 0,
                            PLAYER_ENTITY_SPEED)
projectile_entities = []
potion_entities = [WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_COLOR) for pos in potion_positions]
enemies = [Enemy(WorldEntity(pos, ENEMY_SIZE, ENEMY_COLOR, Direction.LEFT, ENEMY_SPEED, ENEMY_SPEED), 2, 2)
           for pos in enemy_positions]
player_stats = PlayerStats(3, 20, 50, 100)
ticks_since_ai_ran = 0
AI_RUN_INTERVAL = 750

health_potions = {
    1: True,
    2: False,
    3: True,
    4: True,
    5: True
}

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
                if player_stats.mana >= HEAL_ABILITY_MANA_COST:
                    player_stats.lose_mana(HEAL_ABILITY_MANA_COST)
                    player_stats.gain_health(HEAL_ABILITY_AMOUNT)
            elif event.key == pygame.K_f:
                if player_stats.mana >= ATTACK_ABILITY_MANA_COST:
                    player_stats.lose_mana(ATTACK_ABILITY_MANA_COST)
                    proj_pos = (player_entity.x + player_entity.w / 2 - ATTACK_PROJECTILE_SIZE[0] / 2,
                                player_entity.y + player_entity.h / 2 - ATTACK_PROJECTILE_SIZE[1] / 2)
                    projectile_entities.append(
                        WorldEntity(proj_pos, ATTACK_PROJECTILE_SIZE, COLOR_ATTACK_PROJECTILE,
                                    player_entity.direction, ATTACK_PROJECTILE_SPEED, ATTACK_PROJECTILE_SPEED))
            elif event.key == pygame.K_1:
                try_use_health_potion(1)
            elif event.key == pygame.K_2:
                try_use_health_potion(2)
            elif event.key == pygame.K_3:
                try_use_health_potion(3)
            elif event.key == pygame.K_4:
                try_use_health_potion(4)
            elif event.key == pygame.K_5:
                try_use_health_potion(5)
        if event.type == pygame.KEYUP:
            if event.key in PYGAME_MOVEMENT_KEYS:
                movement_keys_down.remove(event.key)
        if movement_keys_down:
            last_pressed_movement_key = movement_keys_down[-1]
            player_entity.set_moving_in_dir(DIRECTION_BY_PYGAME_MOVEMENT_KEY[last_pressed_movement_key])
        else:
            player_entity.set_not_moving()

    # ------------------------------------
    #         RUN ENEMY AI
    # ------------------------------------

    clock.tick()
    ticks_since_ai_ran += clock.get_time()
    if ticks_since_ai_ran > AI_RUN_INTERVAL:
        ticks_since_ai_ran = 0
        for e in enemies:
            e.run_ai_with_target(player_entity)

    # ------------------------------------
    #         UPDATE MOVING ENTITIES
    # ------------------------------------

    for e in enemies:
        # Enemies shouldn't move towards player when they are out of sight
        if boxes_intersect(e.world_entity, camera_world_area):
            update_world_entity_position_within_game_boundary(e.world_entity)
    update_world_entity_position_within_game_boundary(player_entity)

    # ------------------------------------
    #         HANDLE COLLISIONS
    # ------------------------------------

    projectiles_to_delete = []
    potions_to_delete = []
    enemies_to_delete = []
    for projectile in projectile_entities:
        update_world_entity_position(projectile)
        if not boxes_intersect(projectile, ENTIRE_WORLD_AREA):
            projectiles_to_delete.append(projectile)
    for potion in potion_entities:
        if boxes_intersect(player_entity, potion):
            did_pick_up = try_pick_up_potion()
            if did_pick_up:
                potions_to_delete.append(potion)
    for enemy in enemies:
        if boxes_intersect(player_entity, enemy.world_entity):
            enemies_to_delete.append(enemy)
            player_stats.lose_health(2)
        for projectile in projectile_entities:
            if boxes_intersect(enemy.world_entity, projectile):
                enemy.health -= 1
                if enemy.health <= 0:
                    enemies_to_delete.append(enemy)
                projectiles_to_delete.append(projectile)
    projectile_entities = [p for p in projectile_entities if p not in projectiles_to_delete]
    potion_entities = [p for p in potion_entities if p not in potions_to_delete]
    enemies = [e for e in enemies if e not in enemies_to_delete]

    # ------------------------------------
    #         REGEN MANA
    # ------------------------------------

    player_stats.gain_mana(PLAYER_MANA_REGEN)

    # ------------------------------------
    #         UPDATE CAMERA POSITION
    # ------------------------------------

    camera_world_area.x = min(max(player_entity.x - CAMERA_SIZE[0] / 2, 0), GAME_WORLD_SIZE[0] - CAMERA_SIZE[0])
    camera_world_area.y = min(max(player_entity.y - CAMERA_SIZE[1] / 2, 0), GAME_WORLD_SIZE[1] - CAMERA_SIZE[1])

    # ------------------------------------
    #         RENDER EVERYTHING
    # ------------------------------------

    screen.fill(COLOR_BACKGROUND)
    for potion in potion_entities + [e.world_entity for e in enemies] + [p for p in projectile_entities]:
        render_entity(screen, potion, camera_world_area)

    render_entity(screen, player_entity, camera_world_area)
    render_circle(screen, player_entity, camera_world_area)

    for enemy in enemies:
        render_stat_bar(screen, enemy.world_entity.x - camera_world_area.x + 1,
                        enemy.world_entity.y - camera_world_area.y - 10,
                        enemy.world_entity.w - 2, 5, enemy.health, enemy.max_health, COLOR_RED)

    pygame.draw.rect(screen, COLOR_BLACK, (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
    pygame.draw.rect(screen, COLOR_BLACK, (0, CAMERA_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))

    screen.blit(FONT_LARGE.render("Health", False, COLOR_WHITE), (UI_SCREEN_AREA.x + 10, UI_SCREEN_AREA.y + 10))
    render_stat_bar(screen, UI_SCREEN_AREA.x + 10, UI_SCREEN_AREA.y + 40, 100, 25, player_stats.health,
                    player_stats.max_health, COLOR_RED)
    health_text = str(player_stats.health) + "/" + str(player_stats.max_health)
    screen.blit(FONT_LARGE.render(health_text, False, COLOR_WHITE), (UI_SCREEN_AREA.x + 30, UI_SCREEN_AREA.y + 43))

    screen.blit(FONT_LARGE.render("Mana", False, COLOR_WHITE), (UI_SCREEN_AREA.x + 130, UI_SCREEN_AREA.y + 10))
    render_stat_bar(screen, UI_SCREEN_AREA.x + 130, UI_SCREEN_AREA.y + 40, 100, 25, player_stats.mana,
                    player_stats.max_mana, COLOR_BLUE)
    mana_text = str(player_stats.mana) + "/" + str(player_stats.max_mana)
    screen.blit(FONT_LARGE.render(mana_text, False, COLOR_WHITE), (UI_SCREEN_AREA.x + 150, UI_SCREEN_AREA.y + 43))

    screen.blit(FONT_LARGE.render("Potions", False, COLOR_WHITE), (UI_SCREEN_AREA.x + 250, UI_SCREEN_AREA.y + 10))
    render_ui_potion(screen, UI_SCREEN_AREA.x + 250, UI_SCREEN_AREA.y + 39, 27, 27, 1)
    render_ui_potion(screen, UI_SCREEN_AREA.x + 280, UI_SCREEN_AREA.y + 39, 27, 27, 2)
    render_ui_potion(screen, UI_SCREEN_AREA.x + 310, UI_SCREEN_AREA.y + 39, 27, 27, 3)
    render_ui_potion(screen, UI_SCREEN_AREA.x + 340, UI_SCREEN_AREA.y + 39, 27, 27, 4)
    render_ui_potion(screen, UI_SCREEN_AREA.x + 370, UI_SCREEN_AREA.y + 39, 27, 27, 5)

    ui_text = "['A' to heal (" + str(HEAL_ABILITY_MANA_COST) + ")] " + \
              "['F' to attack (" + str(ATTACK_ABILITY_MANA_COST) + ")]"
    text_surface = FONT_SMALL.render(ui_text, False, COLOR_WHITE)
    screen.blit(text_surface, (UI_SCREEN_AREA.x + 20, UI_SCREEN_AREA.y + 75))

    pygame.draw.rect(screen, COLOR_WHITE, UI_SCREEN_AREA.rect(), 1)
    pygame.display.update()
