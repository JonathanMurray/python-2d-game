#!/usr/bin/env python3

import pygame
import sys

from abilities import try_use_ability, ATTACK_PROJECTILE_SIZE, AOE_PROJECTILE_SIZE
from game_world_init import init_game_state_from_file
from user_input import *
from view import View, ScreenArea, SpriteInitializer
from enemy_behavior import run_ai_for_enemy_against_target
from potions import apply_potion_effect

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 500)
PLAYER_ENTITY_SIZE = (60, 60)
ENEMY_ENTITY_SIZE = (30, 30)
ENEMY_2_ENTITY_SIZE = (60, 60)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE, PLAYER_ENTITY_SIZE, ENEMY_ENTITY_SIZE,
                                       ENEMY_2_ENTITY_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
initializers_by_sprite = {
    Sprite.PLAYER: SpriteInitializer("resources/player.png", PLAYER_ENTITY_SIZE),
    Sprite.ENEMY: SpriteInitializer("resources/enemy.png", ENEMY_ENTITY_SIZE),
    Sprite.ENEMY_2: SpriteInitializer("resources/enemy2.png", ENEMY_2_ENTITY_SIZE),
    Sprite.FIREBALL: SpriteInitializer("resources/fireball.png", ATTACK_PROJECTILE_SIZE),
    Sprite.WHIRLWIND: SpriteInitializer("resources/whirlwind.png", AOE_PROJECTILE_SIZE)
}
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE, initializers_by_sprite)
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
        elif isinstance(action, ActionTryUseAbility):
            try_use_ability(game_state, action.ability_type)
        elif isinstance(action, ActionTryUsePotion):
            potion_type = game_state.player_state.try_use_potion(action.slot_number)
            if potion_type:
                apply_potion_effect(potion_type, game_state)
        elif isinstance(action, ActionMoveInDirection):
            game_state.player_entity.set_moving_in_dir(action.direction)
        elif isinstance(action, ActionStopMoving):
            game_state.player_entity.set_not_moving()

    # ------------------------------------
    #         RUN ENEMY AI
    # ------------------------------------

    clock.tick()
    time_passed = clock.get_time()
    ticks_since_ai_ran += time_passed
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
        projectile.world_entity.update_position_according_to_dir_and_speed()

    # ------------------------------------
    #         HANDLE COLLISIONS
    # ------------------------------------

    entities_to_remove = []
    for projectile in game_state.projectile_entities:
        projectile.notify_time_passed(time_passed)
        if projectile.has_expired:
            entities_to_remove.append(projectile)
        if not game_state.is_within_game_world(projectile.world_entity):
            entities_to_remove.append(projectile)
    for potion in game_state.potions:
        if boxes_intersect(game_state.player_entity, potion.world_entity):
            did_pick_up = game_state.player_state.try_pick_up_potion(potion.potion_type)
            if did_pick_up:
                entities_to_remove.append(potion)
    for enemy in game_state.enemies:
        if boxes_intersect(game_state.player_entity, enemy.world_entity):
            entities_to_remove.append(enemy)
            game_state.player_state.lose_health(2)
            game_state.player_state.has_effect_poison = True
            game_state.player_state.time_until_poison_expires = 2000
        for projectile in game_state.get_all_active_projectiles_that_intersect_with(enemy.world_entity):
            enemy.health -= 1
            if enemy.health <= 0:
                entities_to_remove.append(enemy)
            entities_to_remove.append(projectile)
    game_state.remove_entities(entities_to_remove)

    # ------------------------------------
    #         REGEN MANA
    # ------------------------------------

    game_state.player_state.gain_mana(game_state.player_state.mana_regen)
    # TODO Generalise handling of effects that can expire
    if game_state.player_state.has_effect_healing_over_time:
        game_state.player_state.gain_health(1)
        game_state.player_state.time_until_effect_expires -= time_passed
        if game_state.player_state.time_until_effect_expires <= 0:
            game_state.player_state.has_effect_healing_over_time = False
    if game_state.player_state.has_effect_poison:
        game_state.player_state.lose_health(1)
        game_state.player_state.time_until_poison_expires -= time_passed
        if game_state.player_state.time_until_poison_expires <= 0:
            game_state.player_state.has_effect_poison = False
    if game_state.player_state.has_effect_speed:
        game_state.player_state.time_until_speed_expires -= time_passed
        if game_state.player_state.time_until_speed_expires <= 0:
            game_state.player_state.has_effect_speed = False
            game_state.player_entity.add_to_speed_multiplier(- 1)

    # ------------------------------------
    #         UPDATE CAMERA POSITION
    # ------------------------------------

    game_state.center_camera_on_player()

    # ------------------------------------
    #         RENDER EVERYTHING
    # ------------------------------------

    view.render_everything(all_entities=game_state.get_all_entities(),
                           camera_world_area=game_state.camera_world_area,
                           enemies=game_state.enemies,
                           player_health=game_state.player_state.health,
                           player_max_health=game_state.player_state.max_health,
                           player_mana=game_state.player_state.mana,
                           player_max_mana=game_state.player_state.max_mana,
                           potion_slots=game_state.player_state.potion_slots,
                           has_effect_healing_over_time=game_state.player_state.has_effect_healing_over_time,
                           time_until_effect_expires=game_state.player_state.time_until_effect_expires,
                           has_effect_poison=game_state.player_state.has_effect_poison,
                           time_until_poison_expires=game_state.player_state.time_until_poison_expires,
                           has_effect_speed=game_state.player_state.has_effect_speed,
                           time_until_speed_expires=game_state.player_state.time_until_speed_expires)
