import sys
from typing import Optional, Any, List, Tuple

import pygame

import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, SoundId, SceneId, AbstractScene, SceneTransition
from pythongame.core.game_data import CONSUMABLES, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    ConsumableOnGround, ItemOnGround, Chest
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.math import get_directions_to_position
from pythongame.core.npc_behaviors import invoke_npc_action
from pythongame.core.sound_player import play_sound, toggle_muted
from pythongame.core.user_input import ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_dialog_user_inputs, \
    ActionChangeDialogOption, ActionSaveGameState, ActionPressShiftKey, ActionReleaseShiftKey, PlayingUserInputHandler, \
    ActionToggleUiTalents, ActionToggleUiStats, ActionToggleUiControls, ActionRightMouseClicked
from pythongame.core.view.game_world_view import GameWorldView, EntityActionText
from pythongame.core.world_behavior import AbstractWorldBehavior
from pythongame.player_file import save_to_file
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState, UiToggle
from pythongame.scenes_game.game_ui_view import GameUiView
from pythongame.scenes_game.player_environment_interactions import PlayerInteractionsState
from pythongame.scenes_game.playing_ui_controller import PlayingUiController, EventTriggeredFromUi, \
    DragItemBetweenInventorySlots, DropItemOnGround, DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable, TrySwitchItemInInventory, ToggleSound


class PlayingScene(AbstractScene):
    def __init__(self, world_view: GameWorldView):
        self.player_interactions_state = PlayerInteractionsState()
        self.world_view = world_view
        self.render_hit_and_collision_boxes = False
        self.is_shift_key_held_down = False
        self.total_time_played = 0

        # Set on initialization
        self.game_state: GameState = None
        self.game_engine: GameEngine = None
        self.world_behavior: AbstractWorldBehavior = None
        self.ui_state: GameUiState = None
        self.ui_controller: PlayingUiController = None
        self.ui_view: GameUiView = None
        self.user_input_handler = PlayingUserInputHandler()

    def initialize(self, data: Tuple[GameState, GameEngine, AbstractWorldBehavior, GameUiState, GameUiView, bool]):
        if data is not None:
            self.game_state, self.game_engine, self.world_behavior, self.ui_state, self.ui_view, new_hero_was_created = data
            self.ui_controller = PlayingUiController(self.ui_view, self.ui_state)
            self.world_behavior.on_startup(new_hero_was_created)
        # In case this scene has been running before, we make sure to clear any state. Otherwise keys that were held
        # down would still be considered active!
        self.user_input_handler = PlayingUserInputHandler()

    def run_one_frame(self, time_passed: Millis) -> Optional[SceneTransition]:

        self.total_time_played += time_passed

        transition_to_pause = False

        if not self.ui_controller.has_open_dialog():
            self.player_interactions_state.handle_nearby_entities(
                self.game_state.player_entity, self.game_state, self.game_engine)

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        events_triggered_from_ui: List[EventTriggeredFromUi] = []

        if self.ui_controller.has_open_dialog():
            self.game_state.player_entity.set_not_moving()
            user_actions = get_dialog_user_inputs()
            for action in user_actions:
                if isinstance(action, ActionExitGame):
                    exit_game()
                if isinstance(action, ActionChangeDialogOption):
                    self.ui_controller.change_dialog_option(action.index_delta)
                    play_sound(SoundId.DIALOG)
                if isinstance(action, ActionPressSpaceKey):
                    result = self.ui_controller.handle_space_click()
                    if result:
                        npc_in_dialog, option_index = result
                        message = invoke_npc_action(npc_in_dialog.npc_type, option_index, self.game_state)
                        if message:
                            self.ui_state.set_message(message)
                        npc_in_dialog.stun_status.remove_one()
        else:
            user_actions = self.user_input_handler.get_main_user_inputs()
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
                    self.ui_controller.handle_mouse_movement(action.mouse_screen_position)
                if isinstance(action, ActionMouseClicked):
                    events_triggered_from_ui += self.ui_controller.handle_mouse_click(self.game_state.player_state)
                if isinstance(action, ActionMouseReleased):
                    events_triggered_from_ui += self.ui_controller.handle_mouse_release(
                        self.game_state)
                if isinstance(action, ActionRightMouseClicked):
                    events_triggered_from_ui += self.ui_controller.handle_mouse_right_click()
                if isinstance(action, ActionPressSpaceKey):
                    ready_entity = self.player_interactions_state.get_entity_to_interact_with()
                    if ready_entity is not None:
                        if isinstance(ready_entity, NonPlayerCharacter):
                            ready_entity.world_entity.direction = get_directions_to_position(
                                ready_entity.world_entity, self.game_state.player_entity.get_center_position())[0]
                            ready_entity.world_entity.set_not_moving()
                            ready_entity.stun_status.add_one()
                            self.ui_controller.start_dialog_with_npc(ready_entity)
                            play_sound(SoundId.DIALOG)
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
                if isinstance(action, ActionToggleUiTalents):
                    self.ui_view.on_click_toggle(UiToggle.TALENTS)
                    play_sound(SoundId.UI_TOGGLE)
                if isinstance(action, ActionToggleUiStats):
                    self.ui_view.on_click_toggle(UiToggle.STATS)
                    play_sound(SoundId.UI_TOGGLE)
                if isinstance(action, ActionToggleUiControls):
                    self.ui_view.on_click_toggle(UiToggle.CONTROLS)
                    play_sound(SoundId.UI_TOGGLE)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        scene_transition = self.world_behavior.control(time_passed)
        engine_events = self.game_engine.run_one_frame(time_passed)
        for event in engine_events:
            scene_transition = self.world_behavior.handle_event(event)

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
            camera_world_area=self.game_state.get_camera_world_area_including_camera_shake(),
            non_player_characters=self.game_state.non_player_characters,
            visual_effects=self.game_state.visual_effects,
            render_hit_and_collision_boxes=self.render_hit_and_collision_boxes,
            player_health=self.game_state.player_state.health_resource.value,
            player_max_health=self.game_state.player_state.health_resource.max_value,
            entire_world_area=self.game_state.entire_world_area,
            entity_action_text=entity_action_text)

        self.ui_controller.render()

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
                play_sound(SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND)
            elif isinstance(event, DragConsumableBetweenInventorySlots):
                self.game_engine.drag_consumable_between_inventory_slots(event.from_slot, event.to_slot)
                play_sound(SoundId.UI_ITEM_WAS_MOVED)
            elif isinstance(event, DropConsumableOnGround):
                self.game_engine.drop_consumable_on_ground(event.from_slot, event.world_position)
                play_sound(SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND)
            elif isinstance(event, PickTalent):
                name_of_picked = pick_talent(self.game_state, event.option_index)
                if not self.game_state.player_state.has_unpicked_talents():
                    self.ui_view.close_talent_toggle()
                self.ui_state.set_message("Talent picked: " + name_of_picked)
                play_sound(SoundId.EVENT_PICKED_TALENT)
            elif isinstance(event, TrySwitchItemInInventory):
                did_switch_succeed = self.game_engine.try_switch_item_at_slot(event.slot)
                if did_switch_succeed:
                    play_sound(SoundId.UI_ITEM_WAS_MOVED)
                else:
                    play_sound(SoundId.INVALID_ACTION)
            elif isinstance(event, ToggleSound):
                toggle_muted()
            else:
                raise Exception("Unhandled event: " + str(event))

        self.world_view.update_display()

        if scene_transition is not None:
            return scene_transition
        if transition_to_pause:
            return SceneTransition(SceneId.PAUSED, (self.game_state, self.ui_state))
        return None


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
