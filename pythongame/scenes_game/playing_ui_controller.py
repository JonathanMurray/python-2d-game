from typing import Optional, Tuple, List

from pythongame.core.game_state import GameState
from pythongame.core.npc_behaviors import DialogGraphics
from pythongame.core.talents import talents_graphics_from_state
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, ItemSlot, ConsumableSlot, MouseDrag


class EventTriggeredFromUi:
    pass


class DragItemBetweenInventorySlots(EventTriggeredFromUi):
    def __init__(self, from_slot: int, to_slot: int):
        self.from_slot = from_slot
        self.to_slot = to_slot


class DropItemOnGround(EventTriggeredFromUi):
    def __init__(self, from_slot: int, world_position: Tuple[int, int]):
        self.from_slot = from_slot
        self.world_position = world_position


class DragConsumableBetweenInventorySlots(EventTriggeredFromUi):
    def __init__(self, from_slot: int, to_slot: int):
        self.from_slot = from_slot
        self.to_slot = to_slot


class DropConsumableOnGround(EventTriggeredFromUi):
    def __init__(self, from_slot: int, world_position: Tuple[int, int]):
        self.from_slot = from_slot
        self.world_position = world_position


class PickTalent(EventTriggeredFromUi):
    def __init__(self, option_index: int):
        self.option_index = option_index


class StartDraggingItemOrConsumable(EventTriggeredFromUi):
    pass


class TrySwitchItemInInventory(EventTriggeredFromUi):
    def __init__(self, slot: int):
        self.slot = slot


class ClickUiToggle(EventTriggeredFromUi):
    pass


def get_mouse_world_pos(game_state: GameState, mouse_screen_position: Tuple[int, int]):
    return (int(mouse_screen_position[0] + game_state.camera_world_area.x),
            int(mouse_screen_position[1] + game_state.camera_world_area.y))

# TODO
# Fix state handling of view code
# Currently there are:

# ScenePlaying
#   mouse screen position
# PlayingUiController
#   item/consumable being dragged
# GameUiState
#   map, toggles state, time info (highlight), message
# GameUiView
#   player data like abilities, consumables, items, stats, talents


# To fix:
# move mouse screen position downwards (no UI state in scenePlaying)
#

class PlayingUiController:

    def __init__(
            self,
            ui_view: GameUiView,
            ui_state: GameUiState):
        self.game_ui_view = ui_view
        self.ui_state = ui_state
        self.item_slot_being_dragged: Optional[ItemSlot] = None
        self.consumable_slot_being_dragged: Optional[ConsumableSlot] = None

    def render_and_handle_mouse(
            self, game_state: GameState, text_in_topleft_corner: str, dialog_graphics: DialogGraphics,
            mouse_screen_pos: Tuple[int, int], mouse_was_just_clicked: bool,
            mouse_was_just_released: bool, right_mouse_was_just_clicked: bool) -> List[EventTriggeredFromUi]:

        triggered_events: List[EventTriggeredFromUi] = []

        player_state = game_state.player_state

        # UPDATING UI COMPONENTS
        self.game_ui_view.update_abilities(player_state.abilities)
        self.game_ui_view.update_consumables(player_state.consumable_inventory.consumables_in_slots)
        self.game_ui_view.update_inventory(player_state.item_inventory.slots)
        self.game_ui_view.update_regen(player_state.health_resource.get_effective_regen(),
                                       player_state.mana_resource.get_effective_regen())
        self.game_ui_view.update_has_unseen_talents(self.ui_state.talent_toggle_has_unseen_talents)
        self.game_ui_view.update_talents(talents_graphics_from_state(
            player_state.talents_state, player_state.level, player_state.chosen_talent_option_indices))
        self.game_ui_view.update_player_stats(player_state, game_state.player_entity.get_speed_multiplier())

        mouse_hover_event = self.game_ui_view.handle_mouse(mouse_screen_pos, self.ui_state.toggle_enabled)

        # DRAGGING ITEMS
        hovered_item_slot = mouse_hover_event.item
        if mouse_was_just_clicked and hovered_item_slot is not None:
            if hovered_item_slot.item_type:
                self.item_slot_being_dragged = hovered_item_slot
                triggered_events.append(StartDraggingItemOrConsumable())
        if right_mouse_was_just_clicked and hovered_item_slot is not None:
            triggered_events.append(TrySwitchItemInInventory(hovered_item_slot.slot_number))
            self.item_slot_being_dragged = None
        if mouse_was_just_released and self.item_slot_being_dragged is not None:
            if hovered_item_slot is not None and self.item_slot_being_dragged.slot_number != hovered_item_slot.slot_number:
                triggered_events.append(DragItemBetweenInventorySlots(
                    self.item_slot_being_dragged.slot_number, hovered_item_slot.slot_number))
            if not mouse_hover_event.is_over_ui:
                event = DropItemOnGround(
                    self.item_slot_being_dragged.slot_number, get_mouse_world_pos(game_state, mouse_screen_pos))
                triggered_events.append(event)
            self.item_slot_being_dragged = None

        # DRAGGING CONSUMABLES
        hovered_consumable_slot = mouse_hover_event.consumable
        if mouse_was_just_clicked and hovered_consumable_slot is not None:
            if hovered_consumable_slot.consumable_types:
                self.consumable_slot_being_dragged = hovered_consumable_slot
                triggered_events.append(StartDraggingItemOrConsumable())
        if mouse_was_just_released and self.consumable_slot_being_dragged:
            if hovered_consumable_slot and self.consumable_slot_being_dragged.slot_number != hovered_consumable_slot.slot_number:
                event = DragConsumableBetweenInventorySlots(
                    self.consumable_slot_being_dragged.slot_number, hovered_consumable_slot.slot_number)
                triggered_events.append(event)
            if not mouse_hover_event.is_over_ui:
                event = DropConsumableOnGround(
                    self.consumable_slot_being_dragged.slot_number,
                    get_mouse_world_pos(game_state, mouse_screen_pos))
                triggered_events.append(event)
            self.consumable_slot_being_dragged = None

        # UI TOGGLES
        if mouse_was_just_clicked and mouse_hover_event.ui_toggle is not None:
            self.ui_state.notify_toggle_was_clicked(mouse_hover_event.ui_toggle)
            triggered_events.append(ClickUiToggle())

        # PICKING TALENTS
        if mouse_was_just_clicked and mouse_hover_event.talent_choice_option is not None:
            choice_index, option_index = mouse_hover_event.talent_choice_option
            if len(player_state.chosen_talent_option_indices) == choice_index:
                triggered_events.append(PickTalent(option_index))

        # RENDERING
        mouse_drag = None
        if self.consumable_slot_being_dragged or self.item_slot_being_dragged:
            mouse_drag = MouseDrag(self.consumable_slot_being_dragged, self.item_slot_being_dragged, mouse_screen_pos)
        self.game_ui_view.render_ui(
            player_state=player_state,
            ui_state=self.ui_state,
            text_in_topleft_corner=text_in_topleft_corner,
            is_paused=False,
            dialog=dialog_graphics,
            mouse_drag=mouse_drag
        )

        return triggered_events
