import sys
from typing import Optional

import pygame

import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, SoundId, HeroId
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_engine import GameEngine
from pythongame.core.player_environment_interactions import PlayerInteractionsState
from pythongame.core.sound_player import play_sound, init_sound_player
from pythongame.core.user_input import get_user_actions, ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey
from pythongame.core.view import View, MouseHoverEvent
from pythongame.core.view_state import ViewState
from pythongame.game_world_init import create_game_state_from_json_file
from pythongame.register_game_data import register_all_game_data

SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 530)

register_all_game_data()


def main(map_file_name: Optional[str], hero_id: Optional[str], hero_start_level: Optional[int]):
    map_file_name = map_file_name or "map1.json"
    hero_id = HeroId[hero_id] if hero_id else HeroId.MAGE
    hero_start_level = int(hero_start_level) if hero_start_level else 1
    game_state = create_game_state_from_json_file(CAMERA_SIZE, "resources/maps/" + map_file_name, hero_id)
    allocate_input_keys_for_abilities(game_state.player_state.abilities)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)
    view_state = ViewState(game_state.game_world_size)
    clock = pygame.time.Clock()

    init_sound_player()

    game_engine = GameEngine(game_state, view_state)

    is_paused = False
    is_game_over = False
    render_hit_and_collision_boxes = False
    mouse_screen_position = (0, 0)

    game_engine.initialize()

    item_slot_being_dragged: Optional[int] = None
    consumable_slot_being_dragged: Optional[int] = None

    player_interactions_state = PlayerInteractionsState(view_state)

    if hero_start_level > 1:
        game_state.player_state.gain_exp_worth_n_levels(hero_start_level - 1)
        allocate_input_keys_for_abilities(game_state.player_state.abilities)

    while True:

        player_interactions_state.handle_interactions(game_state.player_entity, game_state)

        mouse_was_just_clicked = False
        mouse_was_just_released = False

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        user_actions = get_user_actions()
        for action in user_actions:
            if isinstance(action, ActionExitGame):
                pygame.quit()
                sys.exit()
            if isinstance(action, ActionToggleRenderDebugging):
                render_hit_and_collision_boxes = not render_hit_and_collision_boxes
                # TODO: Handle this better than accessing a global variable from here
                pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING = \
                    not pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING
            if not is_paused and not is_game_over:
                if isinstance(action, ActionTryUseAbility):
                    game_engine.try_use_ability(action.ability_type)
                elif isinstance(action, ActionTryUsePotion):
                    game_engine.try_use_consumable(action.slot_number)
                elif isinstance(action, ActionMoveInDirection):
                    game_engine.move_in_direction(action.direction)
                    player_interactions_state.handle_player_moved()
                elif isinstance(action, ActionStopMoving):
                    game_engine.stop_moving()
            if isinstance(action, ActionPauseGame):
                is_paused = not is_paused
            if isinstance(action, ActionMouseMovement):
                mouse_screen_position = action.mouse_screen_position
            if isinstance(action, ActionMouseClicked):
                mouse_was_just_clicked = True
            if isinstance(action, ActionMouseReleased):
                mouse_was_just_released = True
            if isinstance(action, ActionPressSpaceKey) and not is_game_over:
                player_interactions_state.handle_user_clicked_space(game_state, game_engine)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        clock.tick()
        time_passed = Millis(clock.get_time())

        if not is_paused and not is_game_over:
            player_died = game_engine.run_one_frame(time_passed)
            if player_died:
                play_sound(SoundId.EVENT_PLAYER_DIED)
                is_game_over = True

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        entity_action_text = player_interactions_state.get_action_text()

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            decorations_to_render=game_state.get_decorations_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            non_player_characters=game_state.non_player_characters,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=render_hit_and_collision_boxes,
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            game_world_size=game_state.game_world_size,
            entity_action_text=entity_action_text)

        dialog = player_interactions_state.get_dialog()

        mouse_hover_event: MouseHoverEvent = view.render_ui(
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            player_mana=game_state.player_state.mana,
            player_max_mana=game_state.player_state.max_mana,
            player_health_regen=game_state.player_state.health_regen,
            player_mana_regen=game_state.player_state.mana_regen,
            player_speed_multiplier=game_state.player_entity.speed_multiplier,
            player_life_steal=game_state.player_state.life_steal_ratio,
            consumable_slots=game_state.player_state.consumable_slots,
            player_active_buffs=game_state.player_state.active_buffs,
            fps_string=str(int(clock.get_fps())),
            player_minimap_relative_position=view_state.player_minimap_relative_position,
            abilities=game_state.player_state.abilities,
            message=view_state.message,
            highlighted_consumable_action=view_state.highlighted_consumable_action,
            highlighted_ability_action=view_state.highlighted_ability_action,
            is_paused=is_paused,
            is_game_over=is_game_over,
            ability_cooldowns_remaining=game_state.player_state.ability_cooldowns_remaining,
            item_slots=game_state.player_state.item_slots,
            player_level=game_state.player_state.level,
            mouse_screen_position=mouse_screen_position,
            player_exp=game_state.player_state.exp,
            player_max_exp_in_this_level=game_state.player_state.max_exp_in_this_level,
            dialog=dialog,
            player_money=game_state.player_state.money,
            player_damage_modifier=game_state.player_state.base_damage_modifier + game_state.player_state.damage_modifier_bonus,
            hero_id=game_state.player_state.hero_id)

        # TODO There is a lot of details here about UI state (dragging items). Move that elsewhere.

        hovered_item_slot_number = mouse_hover_event.item_slot_number
        hovered_consumable_slot_number = mouse_hover_event.consumable_slot_number

        if mouse_was_just_clicked and hovered_item_slot_number:
            if game_state.player_state.item_slots[hovered_item_slot_number]:
                item_slot_being_dragged = hovered_item_slot_number

        if item_slot_being_dragged:
            item_type = game_state.player_state.item_slots[item_slot_being_dragged].get_item_type()
            view.render_item_being_dragged(item_type, mouse_screen_position)

        if mouse_was_just_released and item_slot_being_dragged:
            if hovered_item_slot_number and item_slot_being_dragged != hovered_item_slot_number:
                game_engine.switch_inventory_items(item_slot_being_dragged, hovered_item_slot_number)
            if mouse_hover_event.game_world_position:
                game_engine.drop_inventory_item_on_ground(item_slot_being_dragged,
                                                          mouse_hover_event.game_world_position)
            item_slot_being_dragged = False

        if mouse_was_just_clicked and hovered_consumable_slot_number:
            if game_state.player_state.consumable_slots[hovered_consumable_slot_number]:
                consumable_slot_being_dragged = hovered_consumable_slot_number

        if consumable_slot_being_dragged:
            consumable_type = game_state.player_state.consumable_slots[consumable_slot_being_dragged]
            view.render_consumable_being_dragged(consumable_type, mouse_screen_position)

        if mouse_was_just_released and consumable_slot_being_dragged:
            if hovered_consumable_slot_number and consumable_slot_being_dragged != hovered_consumable_slot_number:
                game_engine.switch_consumable_slots(consumable_slot_being_dragged, hovered_consumable_slot_number)
            if mouse_hover_event.game_world_position:
                game_engine.drop_consumable_on_ground(consumable_slot_being_dragged,
                                                      mouse_hover_event.game_world_position)
            consumable_slot_being_dragged = False

        view.update_display()
