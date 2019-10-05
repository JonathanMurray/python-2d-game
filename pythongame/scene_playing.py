import sys
from typing import Optional

import pygame

import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, SoundId, SceneId
from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import GameState
from pythongame.core.player_environment_interactions import PlayerInteractionsState
from pythongame.core.sound_player import play_sound
from pythongame.core.user_input import ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_main_user_inputs, get_dialog_user_inputs, \
    ActionChangeDialogOption, ActionSaveGameState, ActionPressShiftKey, ActionReleaseShiftKey
from pythongame.core.view import MouseHoverEvent, View
from pythongame.core.view_state import ViewState
from pythongame.player_file import save_to_file


class PlayingScene:
    def __init__(
            self,
            player_interactions_state: PlayerInteractionsState,
            game_state: GameState,
            game_engine: GameEngine,
            clock,
            view: View,
            view_state: ViewState):
        self.player_interactions_state = player_interactions_state
        self.game_state = game_state
        self.game_engine = game_engine
        self.clock = clock
        self.view = view
        self.view_state = view_state
        self.render_hit_and_collision_boxes = False
        self.mouse_screen_position = (0, 0)
        self.item_slot_being_dragged: Optional[int] = None
        self.consumable_slot_being_dragged: Optional[int] = None

    def run_one_frame(self):
        scene_transition = None

        self.player_interactions_state.handle_interactions(self.game_state.player_entity, self.game_state)

        mouse_was_just_clicked = False
        mouse_was_just_released = False

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        if self.player_interactions_state.is_player_in_dialog():
            self.game_state.player_entity.set_not_moving()
            user_actions = get_dialog_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    pygame.quit()
                    sys.exit()
                if isinstance(action, ActionChangeDialogOption):
                    self.player_interactions_state.change_dialog_option(action.index_delta)
                if isinstance(action, ActionPressSpaceKey):
                    self.player_interactions_state.handle_user_clicked_space(self.game_state, self.game_engine)
        else:
            user_actions = get_main_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    pygame.quit()
                    sys.exit()
                if isinstance(action, ActionToggleRenderDebugging):
                    self.render_hit_and_collision_boxes = not self.render_hit_and_collision_boxes
                    # TODO: Handle this better than accessing a global variable from here
                    pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING = \
                        not pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING
                if isinstance(action, ActionTryUseAbility):
                    self.game_engine.try_use_ability(action.ability_type)
                elif isinstance(action, ActionTryUsePotion):
                    self.game_engine.try_use_consumable(action.slot_number)
                elif isinstance(action, ActionMoveInDirection):
                    self.game_engine.move_in_direction(action.direction)
                elif isinstance(action, ActionStopMoving):
                    self.game_engine.stop_moving()
                if isinstance(action, ActionPauseGame):
                    scene_transition = SceneId.PAUSED
                if isinstance(action, ActionMouseMovement):
                    self.mouse_screen_position = action.mouse_screen_position
                if isinstance(action, ActionMouseClicked):
                    mouse_was_just_clicked = True
                if isinstance(action, ActionMouseReleased):
                    mouse_was_just_released = True
                if isinstance(action, ActionPressSpaceKey):
                    self.player_interactions_state.handle_user_clicked_space(self.game_state, self.game_engine)
                if isinstance(action, ActionPressShiftKey):
                    self.player_interactions_state.handle_user_pressed_shift()
                if isinstance(action, ActionReleaseShiftKey):
                    self.player_interactions_state.handle_user_released_shift()
                if isinstance(action, ActionSaveGameState):
                    save_to_file(self.game_state)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        self.clock.tick()
        time_passed = Millis(self.clock.get_time())

        self.game_engine.run_one_frame(time_passed)

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        if not self.game_state.player_state.stun_status.is_stunned():
            entity_action_text = self.player_interactions_state.get_action_text()
        else:
            # Don't display any actions on screen if player is stunned. It would look weird when using warp stones
            entity_action_text = None

        self.view.render_world(
            all_entities_to_render=self.game_state.get_all_entities_to_render(),
            decorations_to_render=self.game_state.get_decorations_to_render(),
            player_entity=self.game_state.player_entity,
            is_player_invisible=self.game_state.player_state.is_invisible,
            player_active_buffs=self.game_state.player_state.active_buffs,
            camera_world_area=self.game_state.camera_world_area,
            non_player_characters=self.game_state.non_player_characters,
            visual_effects=self.game_state.visual_effects,
            render_hit_and_collision_boxes=self.render_hit_and_collision_boxes,
            player_health=self.game_state.player_state.health_resource.value,
            player_max_health=self.game_state.player_state.health_resource.max_value,
            entire_world_area=self.game_state.entire_world_area,
            entity_action_text=entity_action_text)

        dialog = self.player_interactions_state.get_dialog()

        # TODO If dragging an item, highlight the inventory slots that are valid for the item?

        mouse_hover_event: MouseHoverEvent = self.view.render_ui(
            player_state=self.game_state.player_state,
            view_state=self.view_state,
            player_speed_multiplier=self.game_state.player_entity.speed_multiplier,
            fps_string=str(int(self.clock.get_fps())),
            is_paused=False,
            mouse_screen_position=self.mouse_screen_position,
            dialog=dialog)

        # TODO There is a lot of details here about UI state (dragging items). Move that elsewhere.

        # DRAGGING ITEMS

        hovered_item_slot_number = mouse_hover_event.item_slot_number

        if mouse_was_just_clicked and hovered_item_slot_number is not None:
            if not self.game_state.player_state.item_inventory.is_slot_empty(hovered_item_slot_number):
                self.item_slot_being_dragged = hovered_item_slot_number
                play_sound(SoundId.UI_START_DRAGGING_ITEM)

        if self.item_slot_being_dragged is not None:
            item_type = self.game_state.player_state.item_inventory.get_item_type_in_slot(self.item_slot_being_dragged)
            self.view.render_item_being_dragged(item_type, self.mouse_screen_position)

        if mouse_was_just_released and self.item_slot_being_dragged is not None:
            if hovered_item_slot_number is not None and self.item_slot_being_dragged != hovered_item_slot_number:
                did_switch_succeed = self.game_engine.drag_item_between_inventory_slots(
                    self.item_slot_being_dragged, hovered_item_slot_number)
                if did_switch_succeed:
                    play_sound(SoundId.UI_ITEM_WAS_MOVED)
                else:
                    play_sound(SoundId.INVALID_ACTION)
            if mouse_hover_event.game_world_position:
                self.game_engine.drop_inventory_item_on_ground(self.item_slot_being_dragged,
                                                               mouse_hover_event.game_world_position)
            self.item_slot_being_dragged = None

        # DRAGGING CONSUMABLES

        hovered_consumable_slot_number = mouse_hover_event.consumable_slot_number

        if mouse_was_just_clicked and hovered_consumable_slot_number is not None:
            if self.game_state.player_state.consumable_inventory.consumables_in_slots[hovered_consumable_slot_number]:
                self.consumable_slot_being_dragged = hovered_consumable_slot_number
                play_sound(SoundId.UI_START_DRAGGING_ITEM)

        if self.consumable_slot_being_dragged is not None:
            consumable_type = self.game_state.player_state.consumable_inventory.consumables_in_slots[
                self.consumable_slot_being_dragged][0]
            self.view.render_consumable_being_dragged(consumable_type, self.mouse_screen_position)

        if mouse_was_just_released and self.consumable_slot_being_dragged is not None:
            if hovered_consumable_slot_number is not None and self.consumable_slot_being_dragged != hovered_consumable_slot_number:
                self.game_engine.drag_consumable_between_inventory_slots(
                    self.consumable_slot_being_dragged, hovered_consumable_slot_number)
                play_sound(SoundId.UI_ITEM_WAS_MOVED)
            if mouse_hover_event.game_world_position:
                self.game_engine.drop_consumable_on_ground(self.consumable_slot_being_dragged,
                                                           mouse_hover_event.game_world_position)
            self.consumable_slot_being_dragged = None

        self.view.update_display()

        return scene_transition
