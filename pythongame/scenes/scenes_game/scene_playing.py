from typing import Optional, Any, List, Tuple, Callable

import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
import pythongame.core.pathfinding.npc_pathfinding
from pythongame.core.common import AbstractWorldBehavior
from pythongame.core.common import Millis, SoundId, AbstractScene, SceneTransition, NpcType, ItemType
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    Chest, Shrine, DungeonEntrance
from pythongame.core.hero_upgrades import pick_talent
from pythongame.core.item_data import plain_item_id
from pythongame.core.math import get_directions_to_position
from pythongame.core.npc_behaviors import select_npc_action, get_dialog_data, blur_npc_action, \
    hover_npc_action
from pythongame.core.sound_player import play_sound, toggle_muted
from pythongame.core.user_input import ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame, ActionToggleRenderDebugging, ActionMouseMovement, \
    ActionMouseClicked, ActionMouseReleased, ActionPressSpaceKey, get_dialog_actions, \
    ActionChangeDialogOption, PlayingUserInputHandler, ActionRightMouseClicked, ActionPressKey
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.world_behavior import DungeonBehavior
from pythongame.leveled_dungeons import create_dungeon_game_state
from pythongame.player_file import SaveFileHandler
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import DragItemBetweenInventorySlots, DropItemOnGround, \
    DragConsumableBetweenInventorySlots, DropConsumableOnGround, \
    PickTalent, StartDraggingItemOrConsumable, TrySwitchItemInInventory, ToggleSound, SaveGame, EventTriggeredFromUi
from pythongame.scenes.scenes_game.game_ui_view import GameUiView
from pythongame.scenes.scenes_game.player_environment_interactions import PlayerInteractionsState
from pythongame.scenes.scenes_game.scene_paused import PausedScene
from pythongame.scenes.scenes_game.ui_events import ToggleFullscreen, ToggleWindow


class PlayingScene(AbstractScene):
    def __init__(self,
                 scene_factory: AbstractSceneFactory,
                 world_view: GameWorldView,
                 game_state: GameState,
                 game_engine: GameEngine,
                 world_behavior: AbstractWorldBehavior,
                 ui_view: GameUiView,
                 new_hero_was_created: bool,
                 character_file: Optional[str],
                 save_file_handler: SaveFileHandler,
                 total_time_played_on_character: Millis,
                 toggle_fullscreen_callback: Callable[[], Any]):

        self.scene_factory = scene_factory
        self.player_interactions_state = PlayerInteractionsState()
        self.world_view = world_view
        self.render_hit_and_collision_boxes = False
        self.game_state: GameState = game_state
        self.game_engine: GameEngine = game_engine
        self.world_behavior: AbstractWorldBehavior = world_behavior
        self.ui_view: GameUiView = ui_view
        self.user_input_handler = PlayingUserInputHandler()
        self.world_behavior.on_startup(new_hero_was_created)
        self.character_file = character_file
        self.save_file_handler = save_file_handler
        self.total_time_played_on_character = total_time_played_on_character
        self.toggle_fullscreen_callback = toggle_fullscreen_callback

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
            self.game_state.game_world.player_entity.set_not_moving()
            user_actions = get_dialog_actions(events)
            for action in user_actions:
                if isinstance(action, ActionChangeDialogOption):
                    npc_type, previous_index, new_index = self.ui_view.change_dialog_option(action.index_delta)
                    self._handle_dialog_change_option(npc_type, previous_index, new_index)
                if isinstance(action, ActionPressSpaceKey):
                    result = self.ui_view.handle_space_click()
                    if result:
                        npc_in_dialog, option_index = result
                        npc_type = npc_in_dialog.npc_type
                        blur_npc_action(npc_type, option_index, self.game_state, self.ui_view)
                        message = select_npc_action(npc_type, option_index, self.game_engine)
                        if message:
                            self.ui_view.info_message.set_message(message)
                        npc_in_dialog.stun_status.remove_one()

                        # User may have been holding down a key when starting dialog, and then releasing it while in
                        # dialog. It's safer then to treat all keys as released when we exit the dialog.
                        self.user_input_handler.forget_held_down_keys()
                if isinstance(action, ActionMouseMovement):
                    self.ui_view.handle_mouse_movement_in_dialog(action.mouse_screen_position)
                    # we handle "normal UI" mouse movement here primarily so that you can hover your equipment
                    # while in a dialog. (especially important when buying from an NPC)
                    self.ui_view.handle_mouse_movement(action.mouse_screen_position)
                if isinstance(action, ActionMouseClicked):
                    result = self.ui_view.handle_mouse_click_in_dialog()
                    if result:
                        npc_type, previous_index, new_index = result
                        self._handle_dialog_change_option(npc_type, previous_index, new_index)

        else:
            user_actions = self.user_input_handler.get_actions(events)
            for action in user_actions:
                if isinstance(action, ActionToggleRenderDebugging):
                    self.render_hit_and_collision_boxes = not self.render_hit_and_collision_boxes
                    # TODO: Handle this better than accessing a global variable from here
                    pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING = \
                        not pythongame.core.pathfinding.npc_pathfinding.DEBUG_RENDER_PATHFINDING
                elif isinstance(action, ActionTryUseAbility):
                    self.game_engine.try_use_ability(action.ability_type)
                elif isinstance(action, ActionTryUsePotion):
                    self.game_engine.try_use_consumable(action.slot_number)
                elif isinstance(action, ActionMoveInDirection):
                    self.game_engine.move_in_direction(action.direction)
                elif isinstance(action, ActionStopMoving):
                    self.game_engine.stop_moving()
                elif isinstance(action, ActionPauseGame):
                    transition_to_pause = True
                elif isinstance(action, ActionMouseMovement):
                    self.ui_view.handle_mouse_movement(action.mouse_screen_position)
                elif isinstance(action, ActionMouseClicked):
                    events_triggered_from_ui += self.ui_view.handle_mouse_click()
                elif isinstance(action, ActionMouseReleased):
                    events_triggered_from_ui += self.ui_view.handle_mouse_release()
                elif isinstance(action, ActionRightMouseClicked):
                    events_triggered_from_ui += self.ui_view.handle_mouse_right_click()
                elif isinstance(action, ActionPressSpaceKey):
                    ready_entity = self.player_interactions_state.get_entity_to_interact_with()
                    if ready_entity is not None:
                        if isinstance(ready_entity, NonPlayerCharacter):
                            ready_entity.world_entity.direction = get_directions_to_position(
                                ready_entity.world_entity,
                                self.game_state.game_world.player_entity.get_center_position())[0]
                            ready_entity.world_entity.set_not_moving()
                            ready_entity.stun_status.add_one()
                            npc_type = ready_entity.npc_type
                            dialog_data = get_dialog_data(npc_type, self.game_state)
                            option_index = self.ui_view.start_dialog_with_npc(ready_entity, dialog_data)
                            play_sound(SoundId.DIALOG)
                            hover_npc_action(npc_type, option_index, self.game_state, self.ui_view)
                        elif isinstance(ready_entity, LootableOnGround):
                            self.game_engine.try_pick_up_loot_from_ground(ready_entity)
                        elif isinstance(ready_entity, Portal):
                            self.game_engine.interact_with_portal(ready_entity)
                        elif isinstance(ready_entity, WarpPoint):
                            self.game_engine.use_warp_point(ready_entity)
                        elif isinstance(ready_entity, Chest):
                            self.game_engine.open_chest(ready_entity)
                        elif isinstance(ready_entity, Shrine):
                            self.game_engine.interact_with_shrine(ready_entity)
                        elif isinstance(ready_entity, DungeonEntrance):
                            has_key = self.game_state.player_state.item_inventory.has_item_in_inventory(
                                plain_item_id(ItemType.PORTAL_KEY))
                            if has_key:
                                entering_dungeon_scene = self.scene_factory.switching_game_world(
                                    self.game_engine, self.character_file, self.total_time_played_on_character,
                                    self._create_dungeon_engine_and_behavior)
                                return SceneTransition(entering_dungeon_scene)
                            else:
                                self.ui_view.info_message.set_message("There is a keyhole on the side!")
                        else:
                            raise Exception("Unhandled entity: " + str(ready_entity))
                elif isinstance(action, ActionPressKey):
                    events_triggered_from_ui += self.ui_view.handle_key_press(action.key)

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
                self.ui_view.info_message.set_message("Talent picked: " + name_of_picked)
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
            elif isinstance(event, ToggleFullscreen):
                self.toggle_fullscreen_callback()
            elif isinstance(event, ToggleWindow):
                play_sound(SoundId.UI_TOGGLE)
            else:
                raise Exception("Unhandled event: " + str(event))

        if transition_to_pause:
            return SceneTransition(PausedScene(self, self.world_view, self.ui_view, self.game_state))

    def _create_dungeon_engine_and_behavior(self, previous_engine: GameEngine):
        previous_game_state = previous_engine.game_state
        player_state = previous_game_state.player_state
        new_game_state = create_dungeon_game_state(player_state, previous_game_state.camera_size,
                                                   player_state.dungeon_difficulty_level)
        new_game_engine = GameEngine(new_game_state, self.ui_view.info_message)
        new_behavior = DungeonBehavior(
            self.scene_factory, previous_game_state, new_game_engine, self.ui_view, self.character_file,
            self.total_time_played_on_character)
        return new_game_engine, new_behavior

    def _handle_dialog_change_option(self, npc_type: NpcType, previous_index: int, new_index: int):
        play_sound(SoundId.DIALOG)
        blur_npc_action(npc_type, previous_index, self.game_state, self.ui_view)
        hover_npc_action(npc_type, new_index, self.game_state, self.ui_view)

    def run_one_frame(self, time_passed: Millis) -> Optional[SceneTransition]:

        self.total_time_played_on_character += time_passed

        if not self.ui_view.has_open_dialog():
            self.player_interactions_state.handle_nearby_entities(
                self.game_state.game_world.player_entity, self.game_state, self.game_engine)

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        scene_transition = self.world_behavior.control(time_passed)
        engine_events = self.game_engine.run_one_frame(time_passed)
        self.ui_view.update(time_passed)
        for event in engine_events:
            scene_transition = self.world_behavior.handle_event(event)

        if scene_transition is not None:
            return scene_transition

        return None

    def render(self):

        entity_action_text = None
        # Don't display any actions on screen if player is stunned. It would look weird when using warp stones
        player_state = self.game_state.player_state
        if not player_state.stun_status.is_stunned():
            entity_action_text = self.player_interactions_state.get_entity_action_text(
                self.user_input_handler.is_shift_held_down())

        game_world = self.game_state.game_world
        self.world_view.render_world(
            all_entities_to_render=self.game_state.get_all_entities_to_render(),
            decorations_to_render=self.game_state.get_decorations_to_render(),
            player_entity=game_world.player_entity,
            is_player_invisible=player_state.is_invisible,
            player_active_buffs=player_state.active_buffs,
            camera_world_area=self.game_state.get_camera_world_area_including_camera_shake(),
            non_player_characters=game_world.non_player_characters,
            visual_effects=game_world.visual_effects,
            render_hit_and_collision_boxes=self.render_hit_and_collision_boxes,
            player_health=player_state.health_resource.value,
            player_max_health=player_state.health_resource.max_value,
            entire_world_area=game_world.entire_world_area,
            entity_action_text=entity_action_text)

        self.ui_view.render()

    def _save_game(self):
        play_sound(SoundId.EVENT_SAVED_GAME)
        filename = self.save_file_handler.save_to_file(
            self.game_state.player_state, self.character_file, self.total_time_played_on_character)
        if self.character_file is None:
            # This is relevant when saving a character for the first time. If we didn't update the field, we would
            # be creating a new file everytime we saved.
            self.character_file = filename
        self.ui_view.info_message.set_message("Game was saved.")


def _get_mouse_world_pos(game_state: GameState, mouse_screen_position: Tuple[int, int]):
    return (int(mouse_screen_position[0] + game_state.camera_world_area.x),
            int(mouse_screen_position[1] + game_state.camera_world_area.y))
