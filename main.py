#!/usr/bin/env python3

import pygame
import sys
from common import Direction, boxes_intersect
from game_state import GameState, WorldArea, WorldEntity, Enemy, PlayerAbilityStats


class ScreenArea:
    def __init__(self, pos, size):
        self.x = pos[0]
        self.y = pos[1]
        self.w = size[0]
        self.h = size[1]

    def rect(self):
        return self.x, self.y, self.w, self.h


def render_entity(entity, camera_world_area):
    rect = (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h)
    pygame.draw.rect(SCREEN, entity.color, rect)


def render_circle(entity, camera_world_area):
    rect = (entity.x - camera_world_area.x, entity.y - camera_world_area.y, entity.w, entity.h)
    pygame.draw.ellipse(SCREEN, COLOR_BLUE, rect)


def _render_stat_bar(x, y, w, h, stat, max_stat, color):
    pygame.draw.rect(SCREEN, COLOR_WHITE, (x - 2, y - 2, w + 3, h + 3), 2)
    pygame.draw.rect(SCREEN, color, (x, y, w * stat / max_stat, h))


def render_stat_bar_for_entity(world_entity, h, stat, max_stat, color, camera_world_area):
    _render_stat_bar(world_entity.x - camera_world_area.x + 1,
                     world_entity.y - camera_world_area.y - 10,
                     world_entity.w - 2, h, stat, max_stat, color)


def render_stat_bar_in_ui(x_in_ui, y_in_ui, w, h, stat, max_stat, color):
    x = UI_SCREEN_AREA.x + x_in_ui
    y = UI_SCREEN_AREA.y + y_in_ui
    _render_stat_bar(x, y, w, h, stat, max_stat, color)


def render_ui_potion(x_in_ui, y_in_ui, w, h, potion_number, has_potion):
    x = UI_SCREEN_AREA.x + x_in_ui
    y = UI_SCREEN_AREA.y + y_in_ui
    pygame.draw.rect(SCREEN, (100, 100, 100), (x, y, w, h), 3)
    if has_potion:
        pygame.draw.rect(SCREEN, (250, 50, 50), (x, y, w, h))
    SCREEN.blit(FONT_LARGE.render(str(potion_number), False, COLOR_WHITE), (x + 8, y + 5))


def render_ui_text(font, text, x, y):
    SCREEN.blit(font.render(text, False, COLOR_WHITE), (UI_SCREEN_AREA.x + x, UI_SCREEN_AREA.y + y))


def render_rect(color, rect, width):
    pygame.draw.rect(SCREEN, color, rect, width)


def render_rect_filled(color, rect):
    pygame.draw.rect(SCREEN, color, rect)


def render_everything(all_entities, camera_world_area, player_entity, enemies, player_health, player_max_health,
                      player_mana, player_max_mana, health_potion_slots):
    SCREEN.fill(COLOR_BACKGROUND)
    for entity in all_entities:
        render_entity(entity, camera_world_area)
    render_circle(player_entity, camera_world_area)

    for enemy in enemies:
        render_stat_bar_for_entity(enemy.world_entity, 5, enemy.health, enemy.max_health, COLOR_RED,
                                   camera_world_area)

    render_rect(COLOR_BLACK, (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
    render_rect_filled(COLOR_BLACK, (0, CAMERA_SIZE[1], SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))

    render_ui_text(FONT_LARGE, "Health", 10, 10)
    render_stat_bar_in_ui(10, 40, 100, 25, player_health, player_max_health,
                          COLOR_RED)
    health_text = str(player_health) + "/" + str(player_max_health)
    render_ui_text(FONT_LARGE, health_text, 30, 43)

    render_ui_text(FONT_LARGE, "Mana", 130, 10)
    render_stat_bar_in_ui(130, 40, 100, 25, player_mana, player_max_mana, COLOR_BLUE)
    mana_text = str(player_mana) + "/" + str(player_max_mana)
    render_ui_text(FONT_LARGE, mana_text, 150, 43)

    render_ui_text(FONT_LARGE, "Potions", 250, 10)
    render_ui_potion(250, 39, 27, 27, 1, has_potion=health_potion_slots[1])
    render_ui_potion(280, 39, 27, 27, 2, has_potion=health_potion_slots[2])
    render_ui_potion(310, 39, 27, 27, 3, has_potion=health_potion_slots[3])
    render_ui_potion(340, 39, 27, 27, 4, has_potion=health_potion_slots[4])
    render_ui_potion(370, 39, 27, 27, 5, has_potion=health_potion_slots[5])

    ui_text = "['A' to heal (" + str(HEAL_ABILITY_MANA_COST) + ")] " + \
              "['F' to attack (" + str(ATTACK_ABILITY_MANA_COST) + ")]"
    render_ui_text(FONT_SMALL, ui_text, 20, 75)

    render_rect(COLOR_WHITE, UI_SCREEN_AREA.rect(), 1)
    pygame.display.update()


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
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, PLAYER_ENTITY_COLOR, Direction.RIGHT, 0,
                                PLAYER_ENTITY_SPEED)
    potion_entities = [WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_COLOR) for pos in potion_positions]
    enemies = [Enemy(WorldEntity(pos, ENEMY_SIZE, ENEMY_COLOR, Direction.LEFT, ENEMY_SPEED, ENEMY_SPEED), 2, 2)
               for pos in enemy_positions]
    player_ability_stats = PlayerAbilityStats(HEAL_ABILITY_MANA_COST, HEAL_ABILITY_AMOUNT, ATTACK_ABILITY_MANA_COST,
                                              ATTACK_PROJECTILE_SIZE, COLOR_ATTACK_PROJECTILE, ATTACK_PROJECTILE_SPEED)
    return GameState(player_entity, potion_entities, enemies, CAMERA_SIZE, GAME_WORLD_SIZE, player_ability_stats)


COLOR_ATTACK_PROJECTILE = (200, 5, 200)
COLOR_WHITE = (250, 250, 250)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (250, 0, 0)
COLOR_BLUE = (0, 0, 250)
COLOR_BACKGROUND = (200, 200, 200)

SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 500)
UI_SCREEN_AREA = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
GAME_WORLD_SIZE = (1000, 1000)  # TODO move fully into game_state.py?
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
                game_state.try_use_heal_ability()
            elif event.key == pygame.K_f:
                game_state.try_use_attack_ability()
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
        for projectile in game_state.get_all_projectiles_that_intersect_with(enemy.world_entity):
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

    game_state.center_camera_on_player()

    # ------------------------------------
    #         RENDER EVERYTHING
    # ------------------------------------

    render_everything(game_state.get_all_entities(), game_state.camera_world_area,
                      game_state.player_entity, game_state.enemies, game_state.player_stats.health,
                      game_state.player_stats.max_health, game_state.player_stats.mana, 
                      game_state.player_stats.max_mana, game_state.health_potion_slots)
