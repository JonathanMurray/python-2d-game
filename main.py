#!/usr/bin/env python3

import pygame
import sys
from common import Direction, boxes_intersect
from game_state import GameState, WorldArea, WorldEntity, Enemy, PlayerAbilityStats
from view import View, ScreenArea


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

SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 500)

GAME_WORLD_SIZE = (1000, 1000)  # TODO move fully into game_state.py?
ENTIRE_WORLD_AREA = WorldArea((0, 0), GAME_WORLD_SIZE)

POTION_ENTITY_SIZE = (30, 30)
POTION_ENTITY_COLOR = (50, 200, 50)
ENEMY_SIZE = (30, 30)
ENEMY_COLOR = (250, 0, 0)
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

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE)
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

    view.render_everything(all_entities=game_state.get_all_entities(),
                           camera_world_area=game_state.camera_world_area,
                           player_entity=game_state.player_entity,
                           enemies=game_state.enemies,
                           player_health=game_state.player_stats.health,
                           player_max_health=game_state.player_stats.max_health,
                           player_mana=game_state.player_stats.mana,
                           player_max_mana=game_state.player_stats.max_mana,
                           health_potion_slots=game_state.health_potion_slots,
                           heal_ability_mana_cost=game_state.player_ability_stats.heal_ability_mana_cost,
                           attack_ability_mana_cost=game_state.player_ability_stats.attack_ability_mana_cost)
