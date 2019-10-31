import sys
from typing import Optional, Any, List

import pygame

import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, SoundId, HeroUpgrade, SceneId
from pythongame.core.game_data import CONSUMABLES, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    ConsumableOnGround, ItemOnGround, Chest
from pythongame.core.hero_upgrades import apply_hero_upgrade
from pythongame.core.math import get_directions_to_position
from pythongame.core.npc_behaviors import get_dialog_data, invoke_npc_action, get_dialog_graphics, DialogGraphics
from pythongame.core.sound_player import play_sound
from pythongame.core.user_input import ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_main_user_inputs, get_dialog_user_inputs, \
    ActionChangeDialogOption, ActionSaveGameState, ActionPressShiftKey, ActionReleaseShiftKey
from pythongame.core.view.game_world_view import GameWorldView, EntityActionText
from pythongame.player_file import save_to_file
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView
from pythongame.scenes_game.player_environment_interactions import PlayerInteractionsState
from pythongame.scenes_game.playing_ui_controller import PlayingUiController, EventTriggeredFromUi, \
    DragItemBetweenInventorySlots, DropItemOnGround, DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable


class DialogHandler:
    def __init__(self):
        self.npc_active_in_dialog: NonPlayerCharacter = None
        self.active_dialog_option_index: int = 0

    def change_dialog_option(self, delta: int):
        num_options = len(get_dialog_data(self.npc_active_in_dialog.npc_type).options)
        self.active_dialog_option_index = (self.active_dialog_option_index + delta) % num_options
        play_sound(SoundId.DIALOG)

    def handle_user_clicked_space(self, game_state: GameState, ui_state: GameUiState):
        message = invoke_npc_action(self.npc_active_in_dialog.npc_type, self.active_dialog_option_index,
                                    game_state)
        if message:
            ui_state.set_message(message)
        self.npc_active_in_dialog.stun_status.remove_one()
        self.npc_active_in_dialog = None

    def is_player_in_dialog(self) -> bool:
        return self.npc_active_in_dialog is not None

    def start_dialog_with_npc(self, npc: NonPlayerCharacter, game_state: GameState):
        self.npc_active_in_dialog = npc
        self.npc_active_in_dialog.world_entity.direction = get_directions_to_position(
            self.npc_active_in_dialog.world_entity,
            game_state.player_entity.get_center_position())[0]
        self.npc_active_in_dialog.world_entity.set_not_moving()
        self.npc_active_in_dialog.stun_status.add_one()
        num_dialog_options = len(get_dialog_data(self.npc_active_in_dialog.npc_type).options)
        if self.active_dialog_option_index >= num_dialog_options:
            # If you talk to one NPC, and leave with option 2, then start talking to an NPC that has just one option
            # we'd get an IndexError if we don't clear the index here. Still, it's useful to keep the index in the
            # case that you want to talk to the same NPC rapidly over and over (to buy potions for example)
            self.active_dialog_option_index = 0
        play_sound(SoundId.DIALOG)

    def get_dialog_graphics(self) -> Optional[DialogGraphics]:
        if self.npc_active_in_dialog:
            return get_dialog_graphics(self.npc_active_in_dialog.npc_type, self.active_dialog_option_index)


class PlayingScene:
    def __init__(
            self,
            game_state: GameState,
            game_engine: GameEngine,
            world_view: GameWorldView,
            ui_view: GameUiView,
            ui_state: GameUiState):
        self.player_interactions_state = PlayerInteractionsState()
        self.game_state = game_state
        self.game_engine = game_engine
        self.world_view = world_view
        self.ui_state = ui_state
        self.render_hit_and_collision_boxes = False
        self.mouse_screen_position = (0, 0)
        self.dialog_handler = DialogHandler()
        self.is_shift_key_held_down = False
        self.ui_controller = PlayingUiController(game_state, ui_view, ui_state)
        self.total_time_played = 0

    def run_one_frame(self, time_passed: Millis, fps_string: str) -> Optional[SceneId]:

        self.total_time_played += time_passed

        transition_to_pause = False

        if not self.dialog_handler.is_player_in_dialog():
            self.player_interactions_state.handle_nearby_entities(
                self.game_state.player_entity, self.game_state, self.game_engine)

        mouse_was_just_clicked = False
        mouse_was_just_released = False

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        if self.dialog_handler.is_player_in_dialog():
            self.game_state.player_entity.set_not_moving()
            user_actions = get_dialog_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    exit_game()
                if isinstance(action, ActionChangeDialogOption):
                    self.dialog_handler.change_dialog_option(action.index_delta)
                if isinstance(action, ActionPressSpaceKey):
                    self.dialog_handler.handle_user_clicked_space(self.game_state, self.ui_state)
        else:
            user_actions = get_main_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    exit_game()
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
                    transition_to_pause = True
                if isinstance(action, ActionMouseMovement):
                    self.mouse_screen_position = action.mouse_screen_position
                if isinstance(action, ActionMouseClicked):
                    mouse_was_just_clicked = True
                if isinstance(action, ActionMouseReleased):
                    mouse_was_just_released = True
                if isinstance(action, ActionPressSpaceKey):
                    ready_entity = self.player_interactions_state.get_entity_to_interact_with()
                    if ready_entity is not None:
                        if isinstance(ready_entity, NonPlayerCharacter):
                            self.dialog_handler.start_dialog_with_npc(ready_entity, self.game_state)
                        elif isinstance(ready_entity, LootableOnGround):
                            self.game_engine.try_pick_up_loot_from_ground(ready_entity)
                        elif isinstance(ready_entity, Portal):
                            self.game_engine.interact_with_portal(ready_entity)
                        elif isinstance(ready_entity, WarpPoint):
                            self.game_engine.use_warp_point(ready_entity)
                        elif isinstance(ready_entity, Chest):
                            self.game_engine.open_chest(ready_entity)
                        else:
                            raise Exception("Unhandled entity: " + str(ready_entity))
                if isinstance(action, ActionPressShiftKey):
                    self.is_shift_key_held_down = True
                if isinstance(action, ActionReleaseShiftKey):
                    self.is_shift_key_held_down = False
                if isinstance(action, ActionSaveGameState):
                    save_to_file(self.game_state)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        self.game_engine.run_one_frame(time_passed)

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        entity_action_text = None
        # Don't display any actions on screen if player is stunned. It would look weird when using warp stones
        if not self.game_state.player_state.stun_status.is_stunned():
            ready_entity = self.player_interactions_state.get_entity_to_interact_with()
            if ready_entity is not None:
                entity_action_text = get_entity_action_text(ready_entity, self.is_shift_key_held_down)

        self.world_view.render_world(
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

        dialog = self.dialog_handler.get_dialog_graphics()

        events_triggered_from_ui: List[EventTriggeredFromUi] = self.ui_controller.render_and_handle_mouse(
            fps_string, dialog, self.mouse_screen_position, mouse_was_just_clicked, mouse_was_just_released)

        for event in events_triggered_from_ui:
            if isinstance(event, StartDraggingItemOrConsumable):
                play_sound(SoundId.UI_START_DRAGGING_ITEM)
            elif isinstance(event, DragItemBetweenInventorySlots):
                did_switch_succeed = self.game_engine.drag_item_between_inventory_slots(event.from_slot, event.to_slot)
                if did_switch_succeed:
                    play_sound(SoundId.UI_ITEM_WAS_MOVED)
                else:
                    play_sound(SoundId.INVALID_ACTION)
            elif isinstance(event, DropItemOnGround):
                self.game_engine.drop_inventory_item_on_ground(event.from_slot, event.world_position)
            elif isinstance(event, DragConsumableBetweenInventorySlots):
                self.game_engine.drag_consumable_between_inventory_slots(event.from_slot, event.to_slot)
                play_sound(SoundId.UI_ITEM_WAS_MOVED)
            elif isinstance(event, DropConsumableOnGround):
                self.game_engine.drop_consumable_on_ground(event.from_slot, event.world_position)
            elif isinstance(event, PickTalent):
                apply_hero_upgrade(event.hero_upgrade, self.game_state)
            else:
                raise Exception("Unhandled event: " + str(event))

        self.world_view.update_display()

        if self.game_state.player_state.has_upgrade(HeroUpgrade.HAS_WON_GAME):
            return SceneId.VICTORY_SCREEN
        if transition_to_pause:
            return SceneId.PAUSED
        return None

    def get_mouse_hover_world_pos(self):
        return (int(self.mouse_screen_position[0] + self.game_state.camera_world_area.x),
                int(self.mouse_screen_position[1] + self.game_state.camera_world_area.y))


def get_entity_action_text(ready_entity: Any, is_shift_key_held_down: bool) -> EntityActionText:
    if isinstance(ready_entity, NonPlayerCharacter):
        return EntityActionText(ready_entity.world_entity, "[Space] ...", [])
    elif isinstance(ready_entity, LootableOnGround):
        loot_name = _get_loot_name(ready_entity)
        if is_shift_key_held_down:
            loot_details = _get_loot_details(ready_entity)
        else:
            loot_details = []
        return EntityActionText(ready_entity.world_entity, "[Space] " + loot_name, loot_details)
    elif isinstance(ready_entity, Portal):
        if ready_entity.is_enabled:
            return EntityActionText(ready_entity.world_entity, "[Space] Warp", [])
        else:
            return EntityActionText(ready_entity.world_entity, "[Space] ???", [])
    elif isinstance(ready_entity, WarpPoint):
        return EntityActionText(ready_entity.world_entity, "[Space] Warp", [])
    elif isinstance(ready_entity, Chest):
        return EntityActionText(ready_entity.world_entity, "[Space] Open", [])
    else:
        raise Exception("Unhandled entity: " + str(ready_entity))


def _get_loot_name(lootable: LootableOnGround) -> str:
    if isinstance(lootable, ConsumableOnGround):
        return CONSUMABLES[lootable.consumable_type].name
    if isinstance(lootable, ItemOnGround):
        return ITEMS[lootable.item_type].name


def _get_loot_details(lootable: LootableOnGround) -> List[str]:
    if isinstance(lootable, ConsumableOnGround):
        return [CONSUMABLES[lootable.consumable_type].description]
    if isinstance(lootable, ItemOnGround):
        return ITEMS[lootable.item_type].description_lines


def exit_game():
    pygame.quit()
    sys.exit()
