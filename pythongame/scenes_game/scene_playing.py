from typing import Optional, Any, List, Tuple

import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import Millis, SoundId, AbstractScene, SceneTransition
from pythongame.core.game_data import CONSUMABLES, ITEMS
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    ConsumableOnGround, ItemOnGround, Chest
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.math import get_directions_to_position
from pythongame.core.npc_behaviors import select_npc_action, get_dialog_data, blur_npc_action, \
    hover_npc_action
from pythongame.core.sound_player import play_sound, toggle_muted
from pythongame.core.user_input import ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_dialog_actions, \
    ActionChangeDialogOption, ActionSaveGameState, PlayingUserInputHandler, ActionToggleUiTalents, ActionToggleUiStats, \
    ActionToggleUiHelp, ActionRightMouseClicked
from pythongame.core.view.game_world_view import GameWorldView, EntityActionText
from pythongame.core.world_behavior import AbstractWorldBehavior
from pythongame.player_file import SaveFileHandler
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState, ToggleButtonId
from pythongame.scenes_game.game_ui_view import DragItemBetweenInventorySlots, DropItemOnGround, \
    DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable, TrySwitchItemInInventory, ToggleSound, SaveGame, EventTriggeredFromUi
from pythongame.scenes_game.game_ui_view import GameUiView
from pythongame.scenes_game.player_environment_interactions import PlayerInteractionsState
from pythongame.scenes_game.scene_paused import PausedScene


class PlayingScene(AbstractScene):
    def __init__(self,
                 world_view: GameWorldView,
                 game_state: GameState,
                 game_engine: GameEngine,
                 world_behavior: AbstractWorldBehavior,
                 ui_state: GameUiState,
                 ui_view: GameUiView,
                 new_hero_was_created: bool,
                 character_file: Optional[str],
                 save_file_handler: SaveFileHandler,
                 total_time_played_on_character: Millis):

        self.player_interactions_state = PlayerInteractionsState()
        self.world_view = world_view
        self.render_hit_and_collision_boxes = False
        self.total_time_played = 0
        self.game_state: GameState = game_state
        self.game_engine: GameEngine = game_engine
        self.world_behavior: AbstractWorldBehavior = world_behavior
        self.ui_state: GameUiState = ui_state
        self.ui_view: GameUiView = ui_view
        self.user_input_handler = PlayingUserInputHandler()
        self.world_behavior.on_startup(new_hero_was_created)
        self.character_file = character_file
        self.save_file_handler = save_file_handler
        self.total_time_played_on_character = total_time_played_on_character

    def on_enter(self):
        self.ui_view.set_paused(False)

        # User may have been holding down a key when pausing, and then releasing it while paused. It's safer then to
        # treat all keys as released when we re-enter this state.
        self.user_input_handler.forget_held_down_keys()

    def handle_user_input(self, events: List[Any]) -> Optional[SceneTransition]:

        transition_to_pause = False

        events_triggered_from_ui: List[EventTriggeredFromUi] = []

        # TODO handle dialog/no dialog more explicitly as states, and delegate more things to them (?)

        if self.ui_view.has_open_dialog():
            self.game_state.player_entity.set_not_moving()
            user_actions = get_dialog_actions(events)
            for action in user_actions:
                if isinstance(action, ActionChangeDialogOption):
                    play_sound(SoundId.DIALOG)
                    npc_type, previous_index, new_index = self.ui_view.change_dialog_option(action.index_delta)
                    blur_npc_action(npc_type, previous_index, self.game_state, self.ui_state)
                    hover_npc_action(npc_type, new_index, self.game_state, self.ui_state)
                if isinstance(action, ActionPressSpaceKey):
                    result = self.ui_view.handle_space_click()
                    if result:
                        npc_in_dialog, option_index = result
                        npc_type = npc_in_dialog.npc_type
                        blur_npc_action(npc_type, option_index, self.game_state, self.ui_state)
                        message = select_npc_action(npc_type, option_index, self.game_state)
                        if message:
                            self.ui_state.set_message(message)
                        npc_in_dialog.stun_status.remove_one()

                        # User may have been holding down a key when starting dialog, and then releasing it while in
                        # dialog. It's safer then to treat all keys as released when we exit the dialog.
                        self.user_input_handler.forget_held_down_keys()
        else:
            user_actions = self.user_input_handler.get_actions(events)
            for action in user_actions:
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
                    self.ui_view.handle_mouse_movement(action.mouse_screen_position)
                if isinstance(action, ActionMouseClicked):
                    events_triggered_from_ui += self.ui_view.handle_mouse_click()
                if isinstance(action, ActionMouseReleased):
                    events_triggered_from_ui += self.ui_view.handle_mouse_release()
                if isinstance(action, ActionRightMouseClicked):
                    events_triggered_from_ui += self.ui_view.handle_mouse_right_click()
                if isinstance(action, ActionPressSpaceKey):
                    ready_entity = self.player_interactions_state.get_entity_to_interact_with()
                    if ready_entity is not None:
                        if isinstance(ready_entity, NonPlayerCharacter):
                            ready_entity.world_entity.direction = get_directions_to_position(
                                ready_entity.world_entity, self.game_state.player_entity.get_center_position())[0]
                            ready_entity.world_entity.set_not_moving()
                            ready_entity.stun_status.add_one()
                            npc_type = ready_entity.npc_type
                            dialog_data = get_dialog_data(npc_type)
                            option_index = self.ui_view.start_dialog_with_npc(ready_entity, dialog_data)
                            play_sound(SoundId.DIALOG)
                            hover_npc_action(npc_type, option_index, self.game_state, self.ui_state)
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
                if isinstance(action, ActionSaveGameState):
                    self._save_game()
                if isinstance(action, ActionToggleUiTalents):
                    self.ui_view.click_toggle_button(ToggleButtonId.TALENTS)
                    play_sound(SoundId.UI_TOGGLE)
                if isinstance(action, ActionToggleUiStats):
                    self.ui_view.click_toggle_button(ToggleButtonId.STATS)
                    play_sound(SoundId.UI_TOGGLE)
                if isinstance(action, ActionToggleUiHelp):
                    self.ui_view.click_toggle_button(ToggleButtonId.HELP)
                    play_sound(SoundId.UI_TOGGLE)

        # TODO Much noise below around playing sounds. Perhaps game_engine should play the sounds in these cases?
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
                world_position = _get_mouse_world_pos(self.game_state, event.screen_position)
                self.game_engine.drop_inventory_item_on_ground(event.from_slot, world_position)
                play_sound(SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND)
            elif isinstance(event, DragConsumableBetweenInventorySlots):
                self.game_engine.drag_consumable_between_inventory_slots(event.from_slot, event.to_slot)
                play_sound(SoundId.UI_ITEM_WAS_MOVED)
            elif isinstance(event, DropConsumableOnGround):
                world_position = _get_mouse_world_pos(self.game_state, event.screen_position)
                self.game_engine.drop_consumable_on_ground(event.from_slot, world_position)
                play_sound(SoundId.UI_ITEM_WAS_DROPPED_ON_GROUND)
            elif isinstance(event, PickTalent):
                name_of_picked = pick_talent(self.game_state, event.tier_index, event.option_index)
                if not self.game_state.player_state.has_unpicked_talents():
                    self.ui_view.close_talent_window()
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
            elif isinstance(event, SaveGame):
                self._save_game()
            else:
                raise Exception("Unhandled event: " + str(event))

        if transition_to_pause:
            return SceneTransition(PausedScene(self, self.world_view, self.ui_view, self.game_state, self.ui_state))

    def run_one_frame(self, time_passed: Millis) -> Optional[SceneTransition]:

        self.total_time_played += time_passed
        self.total_time_played_on_character += time_passed

        if not self.ui_view.has_open_dialog():
            self.player_interactions_state.handle_nearby_entities(
                self.game_state.player_entity, self.game_state, self.game_engine)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        scene_transition = self.world_behavior.control(time_passed)
        engine_events = self.game_engine.run_one_frame(time_passed)
        for event in engine_events:
            scene_transition = self.world_behavior.handle_event(event)

        if scene_transition is not None:
            return scene_transition

        return None

    def render(self):

        entity_action_text = None
        # Don't display any actions on screen if player is stunned. It would look weird when using warp stones
        if not self.game_state.player_state.stun_status.is_stunned():
            ready_entity = self.player_interactions_state.get_entity_to_interact_with()
            if ready_entity is not None:
                entity_action_text = _get_entity_action_text(ready_entity, self.user_input_handler.is_shift_held_down())

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

        self.ui_view.render(self.ui_state)

    def _save_game(self):
        play_sound(SoundId.EVENT_SAVED_GAME)
        filename = self.save_file_handler.save_to_file(
            self.game_state, self.character_file, self.total_time_played_on_character)
        if self.character_file is None:
            # This is relevant when saving a character for the first time. If we didn't update the field, we would
            # be creating a new file everytime we saved.
            self.character_file = filename
        self.ui_state.set_message("Game was saved.")


def _get_entity_action_text(ready_entity: Any, is_shift_key_held_down: bool) -> EntityActionText:
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


def _get_mouse_world_pos(game_state: GameState, mouse_screen_position: Tuple[int, int]):
    return (int(mouse_screen_position[0] + game_state.camera_world_area.x),
            int(mouse_screen_position[1] + game_state.camera_world_area.y))
