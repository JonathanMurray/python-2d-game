import datetime
import sys
from typing import Optional

import pygame

import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, HeroId, SoundId
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_engine import GameEngine
from pythongame.core.player_environment_interactions import PlayerInteractionsState
from pythongame.core.sound_player import init_sound_player, play_sound
from pythongame.core.user_input import ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_main_user_inputs, get_dialog_user_inputs, \
    ActionChangeDialogOption, ActionSaveGameState
from pythongame.core.view import View, MouseHoverEvent
from pythongame.core.view_state import ViewState
from pythongame.game_world_init import create_game_state_from_json_file, save_game_state_to_json_file
from pythongame.register_game_data import register_all_game_data

SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 530)

register_all_game_data()


def main(map_file_name: Optional[str], hero_id: Optional[str], hero_start_level: Optional[int],
         start_money: Optional[int]):
    map_file_name = map_file_name or "map1.json"
    hero_id = HeroId[hero_id] if hero_id else HeroId.MAGE
    hero_start_level = int(hero_start_level) if hero_start_level else 1
    start_money = int(start_money) if start_money else 0
    game_state = create_game_state_from_json_file(CAMERA_SIZE, "resources/maps/" + map_file_name, hero_id)
    allocate_input_keys_for_abilities(game_state.player_state.abilities)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)
    view_state = ViewState(game_state.entire_world_area)
    clock = pygame.time.Clock()

    init_sound_player()

    game_engine = GameEngine(game_state, view_state)

    is_paused = False

    # TODO Is this flag needed, now that player re-spawns upon death?
    is_game_over = False

    render_hit_and_collision_boxes = False
    mouse_screen_position = (0, 0)

    item_slot_being_dragged: Optional[int] = None
    consumable_slot_being_dragged: Optional[int] = None

    player_interactions_state = PlayerInteractionsState(view_state)

    if hero_start_level > 1:
        game_state.player_state.gain_exp_worth_n_levels(hero_start_level - 1)
        allocate_input_keys_for_abilities(game_state.player_state.abilities)

    if start_money > 0:
        game_state.player_state.money += start_money

    while True:

        player_interactions_state.handle_interactions(game_state.player_entity, game_state)

        mouse_was_just_clicked = False
        mouse_was_just_released = False

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        if player_interactions_state.is_player_in_dialog():
            game_state.player_entity.set_not_moving()
            user_actions = get_dialog_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    pygame.quit()
                    sys.exit()
                if isinstance(action, ActionChangeDialogOption):
                    player_interactions_state.change_dialog_option(action.index_delta)
                if isinstance(action, ActionPressSpaceKey) and not is_game_over:
                    player_interactions_state.handle_user_clicked_space(game_state, game_engine)
        else:
            user_actions = get_main_user_inputs()
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
                if isinstance(action, ActionSaveGameState):
                    filename = "savefiles/DEBUG_" + str(datetime.datetime.now()).replace(" ", "_") + ".json"
                    save_game_state_to_json_file(game_state, filename)
                    print("Saved game state to file: " + filename)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        clock.tick()
        time_passed = Millis(clock.get_time())

        if not is_paused and not is_game_over:
            game_engine.run_one_frame(time_passed)

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        entity_action_text = player_interactions_state.get_action_text()

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            decorations_to_render=game_state.get_decorations_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            player_active_buffs=game_state.player_state.active_buffs,
            camera_world_area=game_state.camera_world_area,
            non_player_characters=game_state.non_player_characters,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=render_hit_and_collision_boxes,
            player_health=game_state.player_state.health_resource.value,
            player_max_health=game_state.player_state.health_resource.max_value,
            entire_world_area=game_state.entire_world_area,
            entity_action_text=entity_action_text)

        dialog = player_interactions_state.get_dialog()

        # TODO If dragging an item, highlight the inventory slots that are valid for the item?

        mouse_hover_event: MouseHoverEvent = view.render_ui(
            player_state=game_state.player_state,
            view_state=view_state,
            player_speed_multiplier=game_state.player_entity.speed_multiplier,
            fps_string=str(int(clock.get_fps())),
            is_paused=is_paused,
            is_game_over=is_game_over,
            mouse_screen_position=mouse_screen_position,
            dialog=dialog)

        # TODO There is a lot of details here about UI state (dragging items). Move that elsewhere.

        # DRAGGING ITEMS

        hovered_item_slot_number = mouse_hover_event.item_slot_number

        if mouse_was_just_clicked and hovered_item_slot_number is not None:
            if not game_state.player_state.item_inventory.is_slot_empty(hovered_item_slot_number):
                item_slot_being_dragged = hovered_item_slot_number
                play_sound(SoundId.UI_START_DRAGGING_ITEM)

        if item_slot_being_dragged is not None:
            item_type = game_state.player_state.item_inventory.get_item_type_in_slot(item_slot_being_dragged)
            view.render_item_being_dragged(item_type, mouse_screen_position)

        if mouse_was_just_released and item_slot_being_dragged is not None:
            if hovered_item_slot_number is not None and item_slot_being_dragged != hovered_item_slot_number:
                did_switch_succeed = game_engine.switch_inventory_items(item_slot_being_dragged,
                                                                        hovered_item_slot_number)
                if did_switch_succeed:
                    play_sound(SoundId.UI_ITEM_WAS_MOVED)
                else:
                    play_sound(SoundId.INVALID_ACTION)
            if mouse_hover_event.game_world_position:
                game_engine.drop_inventory_item_on_ground(item_slot_being_dragged,
                                                          mouse_hover_event.game_world_position)
            item_slot_being_dragged = None

        # DRAGGING CONSUMABLES

        hovered_consumable_slot_number = mouse_hover_event.consumable_slot_number

        if mouse_was_just_clicked and hovered_consumable_slot_number is not None:
            if game_state.player_state.consumable_inventory.consumables_in_slots[hovered_consumable_slot_number]:
                consumable_slot_being_dragged = hovered_consumable_slot_number
                play_sound(SoundId.UI_START_DRAGGING_ITEM)

        if consumable_slot_being_dragged is not None:
            consumable_type = game_state.player_state.consumable_inventory.consumables_in_slots[
                consumable_slot_being_dragged][0]
            view.render_consumable_being_dragged(consumable_type, mouse_screen_position)

        if mouse_was_just_released and consumable_slot_being_dragged is not None:
            if hovered_consumable_slot_number is not None and consumable_slot_being_dragged != hovered_consumable_slot_number:
                game_engine.drag_consumable_between_slots(consumable_slot_being_dragged, hovered_consumable_slot_number)
                play_sound(SoundId.UI_ITEM_WAS_MOVED)
            if mouse_hover_event.game_world_position:
                game_engine.drop_consumable_on_ground(consumable_slot_being_dragged,
                                                      mouse_hover_event.game_world_position)
            consumable_slot_being_dragged = None

        view.update_display()
