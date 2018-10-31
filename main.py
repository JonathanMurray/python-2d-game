#!/usr/bin/env python3

import pygame
import sys

from abilities import apply_ability_effect
from buffs import BUFF_EFFECTS
from game_world_init import init_game_state_from_file
from player_controls import PlayerControls, TryUseAbilityResult
from potions import apply_potion_effect
from user_input import *
from view import View, ScreenArea
from view_state import ViewState

GAME_WORLD_SIZE = (1000, 1000)
SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 400)

game_state = init_game_state_from_file(GAME_WORLD_SIZE, CAMERA_SIZE)
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode(SCREEN_SIZE)
ui_screen_area = ScreenArea((0, CAMERA_SIZE[1]), (SCREEN_SIZE[0], SCREEN_SIZE[1] - CAMERA_SIZE[1]))
view = View(screen, ui_screen_area, CAMERA_SIZE, SCREEN_SIZE)
view_state = ViewState(GAME_WORLD_SIZE)
player_controls = PlayerControls()
clock = pygame.time.Clock()

while True:

    # ------------------------------------
    #         HANDLE USER INPUT
    # ------------------------------------

    user_actions = get_user_actions()
    for action in user_actions:
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        elif isinstance(action, ActionTryUseAbility):
            view_state.notify_ability_was_clicked(action.ability_type)
            result = player_controls.try_use_ability(game_state.player_state, action.ability_type)
            if result == TryUseAbilityResult.SUCCESS:
                apply_ability_effect(game_state, action.ability_type)
            elif result == TryUseAbilityResult.NOT_ENOUGH_MANA:
                view_state.set_message("Not enough mana!")
        elif isinstance(action, ActionTryUsePotion):
            view_state.notify_potion_was_clicked(action.slot_number)
            used_potion_type = game_state.player_state.try_use_potion(action.slot_number)
            if used_potion_type:
                apply_potion_effect(used_potion_type, game_state)
            else:
                view_state.set_message("No potion to use!")
        elif isinstance(action, ActionMoveInDirection):
            game_state.player_entity.set_moving_in_dir(action.direction)
        elif isinstance(action, ActionStopMoving):
            game_state.player_entity.set_not_moving()

    # ------------------------------------
    #     UPDATE STATE BASED ON CLOCK
    # ------------------------------------

    clock.tick()
    time_passed = clock.get_time()

    for e in game_state.enemies:
        # Enemy AI shouldn't run if enemy is out of sight
        if boxes_intersect(e.world_entity, game_state.camera_world_area):
            e.enemy_mind.control_enemy(game_state, e, game_state.player_entity,
                                       game_state.player_state.is_invisible, time_passed)

    view_state.notify_player_entity_center_position(game_state.player_entity.get_center_position())

    player_controls.notify_time_passed(time_passed)

    view_state.notify_time_passed(time_passed)

    game_state.update_and_expire_projectiles(time_passed)

    game_state.remove_dead_enemies()

    buffs_update = game_state.player_state.update_and_expire_buffs(time_passed)
    for buff_type in buffs_update.buffs_that_started:
        BUFF_EFFECTS[buff_type].apply_start_effect(game_state)
    for buff_type in buffs_update.active_buffs:
        BUFF_EFFECTS[buff_type].apply_middle_effect(game_state, time_passed)
    for buff_type in buffs_update.buffs_that_ended:
        BUFF_EFFECTS[buff_type].apply_end_effect(game_state)

    game_state.player_state.regenerate_mana(time_passed)

    for e in game_state.enemies:
        # Enemies shouldn't move towards player when they are out of sight
        if boxes_intersect(e.world_entity, game_state.camera_world_area):
            game_state.update_world_entity_position_within_game_world(e.world_entity, time_passed)
    game_state.update_world_entity_position_within_game_world(game_state.player_entity, time_passed)
    for projectile in game_state.projectile_entities:
        projectile.world_entity.update_position_according_to_dir_and_speed(time_passed)

    # ------------------------------------
    #          HANDLE COLLISIONS
    # ------------------------------------

    entities_to_remove = []
    for potion in game_state.potions_on_ground:
        if boxes_intersect(game_state.player_entity, potion.world_entity):
            did_pick_up = game_state.player_state.try_pick_up_potion(potion.potion_type)
            if did_pick_up:
                entities_to_remove.append(potion)
    for enemy in game_state.enemies:
        for projectile in game_state.get_active_player_projectiles_intersecting_with(enemy.world_entity):
            projectile.projectile_controller.apply_enemy_collision(enemy)
            entities_to_remove.append(projectile)

    for projectile in game_state.get_active_enemy_projectiles_intersecting_with_player():
        projectile.projectile_controller.apply_player_collision(game_state)
        entities_to_remove.append(projectile)

    game_state.remove_entities(entities_to_remove)

    # ------------------------------------
    #       UPDATE CAMERA POSITION
    # ------------------------------------

    game_state.center_camera_on_player()

    # ------------------------------------
    #          RENDER EVERYTHING
    # ------------------------------------

    view.render_everything(all_entities=game_state.get_all_entities(),
                           player_entity=game_state.player_entity,
                           is_player_invisible=game_state.player_state.is_invisible,
                           camera_world_area=game_state.camera_world_area,
                           enemies=game_state.enemies,
                           player_health=game_state.player_state.health,
                           player_max_health=game_state.player_state.max_health,
                           player_mana=game_state.player_state.mana,
                           player_max_mana=game_state.player_state.max_mana,
                           potion_slots=game_state.player_state.potion_slots,
                           player_active_buffs=game_state.player_state.active_buffs,
                           fps_string=view_state.fps_string,
                           player_minimap_relative_position=view_state.player_minimap_relative_position,
                           abilities=[AbilityType.ATTACK, AbilityType.HEAL, AbilityType.AOE_ATTACK],
                           message=view_state.message,
                           highlighted_potion_action=view_state.highlighted_potion_action,
                           highlighted_ability_action=view_state.highlighted_ability_action)
