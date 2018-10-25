#!/usr/bin/env python3

import pygame
import sys

from common import boxes_intersect
from game_world_init import init_game_state_from_file
from user_input import *
from view import View, ScreenArea
from enemy_behavior import run_ai_for_enemy_against_target

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 500)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE)
clock = pygame.time.Clock()
ticks_since_ai_ran = 0
AI_RUN_INTERVAL = 750

while True:

    # ------------------------------------
    #         HANDLE EVENTS
    # ------------------------------------

    user_actions = get_user_actions()
    for action in user_actions:
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        elif isinstance(action, ActionTryUseHealAbility):
            game_state.try_use_heal_ability()
        elif isinstance(action, ActionTryUseAttackAbility):
            game_state.try_use_attack_ability()
        elif isinstance(action, ActionTryUseHealthPotion):
            game_state.player_stats.try_use_potion(action.slot_number)
        elif isinstance(action, ActionMoveInDirection):
            game_state.player_entity.set_moving_in_dir(action.direction)
        elif isinstance(action, ActionStopMoving):
            game_state.player_entity.set_not_moving()

    # ------------------------------------
    #         RUN ENEMY AI
    # ------------------------------------

    clock.tick()
    ticks_since_ai_ran += clock.get_time()
    if ticks_since_ai_ran > AI_RUN_INTERVAL:
        ticks_since_ai_ran = 0
        for e in game_state.enemies:
            direction = run_ai_for_enemy_against_target(e.world_entity, game_state.player_entity, e.enemy_behavior)
            e.world_entity.set_moving_in_dir(direction)

    # ------------------------------------
    #         UPDATE MOVING ENTITIES
    # ------------------------------------

    for e in game_state.enemies:
        # Enemies shouldn't move towards player when they are out of sight
        if boxes_intersect(e.world_entity, game_state.camera_world_area):
            game_state.update_world_entity_position_within_game_world(e.world_entity)
    game_state.update_world_entity_position_within_game_world(game_state.player_entity)
    for projectile in game_state.projectile_entities:
        projectile.update_position_according_to_dir_and_speed()

    # ------------------------------------
    #         HANDLE COLLISIONS
    # ------------------------------------

    entities_to_remove = []
    for projectile in game_state.projectile_entities:
        if not game_state.is_within_game_world(projectile):
            entities_to_remove.append(projectile)
    for potion in game_state.potions:
        if boxes_intersect(game_state.player_entity, potion.world_entity):
            did_pick_up = game_state.player_stats.try_pick_up_potion(potion.potion_type)
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

    game_state.player_stats.gain_mana(game_state.player_stats.mana_regen)

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
                           potion_slots=game_state.player_stats.potion_slots,
                           heal_ability_mana_cost=game_state.player_ability_stats.heal_ability_mana_cost,
                           attack_ability_mana_cost=game_state.player_ability_stats.attack_ability_mana_cost)
