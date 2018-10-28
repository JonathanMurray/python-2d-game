#!/usr/bin/env python3

import pygame
import sys

from abilities import try_use_ability
from buffs import buffs
from enemy_behavior import run_ai_for_enemy_against_target
from game_world_init import init_game_state_from_file
from potions import apply_potion_effect
from user_input import *
from view import View, ScreenArea

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 400)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE)
clock = pygame.time.Clock()
ticks_since_ai_ran = 0
AI_RUN_INTERVAL = 750
MINIMAP_UPDATE_INTERVAL = 1000
ticks_since_minimap_updated = MINIMAP_UPDATE_INTERVAL
player_minimap_relative_position = (0, 0)
recent_frame_durations = []
fps_string = "N/A"

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
            used_potion_type = game_state.player_state.try_use_potion(action.slot_number)
            if used_potion_type:
                apply_potion_effect(used_potion_type, game_state)
        elif isinstance(action, ActionMoveInDirection):
            game_state.player_entity.set_moving_in_dir(action.direction)
        elif isinstance(action, ActionStopMoving):
            game_state.player_entity.set_not_moving()

    # ------------------------------------
    #         RUN THINGS BASED ON CLOCK
    # ------------------------------------

    clock.tick()
    time_passed = clock.get_time()

    recent_frame_durations.append(time_passed)
    num_frames_to_sample_for_fps = 30
    if len(recent_frame_durations) == num_frames_to_sample_for_fps:
        fps_string = str(int(1000 * num_frames_to_sample_for_fps / sum(recent_frame_durations)))
        recent_frame_durations = []

    ticks_since_ai_ran += time_passed
    if ticks_since_ai_ran > AI_RUN_INTERVAL:
        ticks_since_ai_ran = 0
        for e in game_state.enemies:
            direction = run_ai_for_enemy_against_target(e.world_entity, game_state.player_entity, e.enemy_behavior)
            e.world_entity.set_moving_in_dir(direction)

    ticks_since_minimap_updated += time_passed
    if ticks_since_minimap_updated > MINIMAP_UPDATE_INTERVAL:
        ticks_since_minimap_updated = 0
        player_minimap_relative_position = (game_state.player_entity.get_center_x() / game_state.game_world_size[0],
                                            game_state.player_entity.get_center_y() / game_state.game_world_size[1])

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
    for potion in game_state.potions_on_ground:
        if boxes_intersect(game_state.player_entity, potion.world_entity):
            did_pick_up = game_state.player_state.try_pick_up_potion(potion.potion_type)
            if did_pick_up:
                entities_to_remove.append(potion)
    for enemy in game_state.enemies:
        if boxes_intersect(game_state.player_entity, enemy.world_entity):
            entities_to_remove.append(enemy)
            game_state.player_state.lose_health(2)
            game_state.player_state.add_buff(BuffType.DAMAGE_OVER_TIME, 2000)
        for projectile in game_state.get_all_active_projectiles_that_intersect_with(enemy.world_entity):
            enemy.health -= 1
            if enemy.health <= 0:
                entities_to_remove.append(enemy)
            entities_to_remove.append(projectile)
    game_state.remove_entities(entities_to_remove)

    # ------------------------------------
    #         PLAYER EFFECTS
    # ------------------------------------

    game_state.player_state.gain_mana(game_state.player_state.mana_regen)

    buffs_update = game_state.player_state.handle_buffs(time_passed)
    for buff_type in buffs_update.buffs_that_started:
        buffs[buff_type].apply_start_effect(game_state)
    for buff_type in buffs_update.active_buffs:
        buffs[buff_type].apply_middle_effect(game_state)
    for buff_type in buffs_update.buffs_that_ended:
        buffs[buff_type].apply_end_effect(game_state)

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
                           buffs=game_state.player_state.buffs,
                           fps_string=fps_string,
                           player_minimap_relative_position=player_minimap_relative_position,
                           abilities=[AbilityType.ATTACK, AbilityType.HEAL, AbilityType.AOE_ATTACK])
