from typing import Optional, Tuple, List

from pythongame.core.game_state import GameState, PlayerState, NonPlayerCharacter
from pythongame.core.npc_behaviors import get_dialog_data, DialogData
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, DraggedItemSlot, DraggedConsumableSlot, MouseDrag, \
    DialogConfig


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


class ToggleSound(EventTriggeredFromUi):
    pass


class SaveGame(EventTriggeredFromUi):
    pass


class StartDraggingItemOrConsumable(EventTriggeredFromUi):
    pass


class TrySwitchItemInInventory(EventTriggeredFromUi):
    def __init__(self, slot: int):
        self.slot = slot


def get_mouse_world_pos(game_state: GameState, mouse_screen_position: Tuple[int, int]):
    return (int(mouse_screen_position[0] + game_state.camera_world_area.x),
            int(mouse_screen_position[1] + game_state.camera_world_area.y))


# TODO
# Fix state handling of view code
# Currently there are:

# PlayingUiController
#   item/consumable being dragged
# GameUiState
#   map, toggles state, time info (highlight), message
# GameUiView
#   player data like abilities, consumables, items, stats, talents


# To fix:
#

class DialogState:
    def __init__(self):
        self.option_index: int = 0
        self.data: DialogData = None
        self.npc: NonPlayerCharacter = None
        self.active = False


class PlayingUiController:

    def __init__(self, ui_view: GameUiView, ui_state: GameUiState):
        self.ui_view = ui_view
        self.ui_state = ui_state

        self.mouse_screen_position: Tuple[int, int] = (0, 0)
        self.item_slot_being_dragged: Optional[DraggedItemSlot] = None
        self.consumable_slot_being_dragged: Optional[DraggedConsumableSlot] = None
        self.hovered_item_slot: Optional[DraggedItemSlot] = None
        self.hovered_consumable_slot: Optional[DraggedConsumableSlot] = None
        self.hovered_talent_choice_option: Optional[Tuple[int, int]] = None
        self.is_mouse_over_ui: bool = False
        self.dialog = DialogState()

    def render(self):

        # MOUSE HANDLING
        mouse_hover_event = self.ui_view.handle_mouse(self.mouse_screen_position)
        self.hovered_item_slot = mouse_hover_event.item
        self.hovered_consumable_slot = mouse_hover_event.consumable
        self.is_mouse_over_ui = mouse_hover_event.is_over_ui
        self.hovered_talent_choice_option = mouse_hover_event.talent_choice_option

        # RENDERING
        mouse_drag = None
        if self.consumable_slot_being_dragged or self.item_slot_being_dragged:
            mouse_drag = MouseDrag(self.consumable_slot_being_dragged, self.item_slot_being_dragged,
                                   self.mouse_screen_position)
        self.ui_view.render(
            ui_state=self.ui_state,
            is_paused=False,
            mouse_drag=mouse_drag
        )

    def handle_mouse_movement(self, mouse_screen_position: Tuple[int, int]):
        self.mouse_screen_position = mouse_screen_position

    def handle_mouse_right_click(self):
        triggered_events = []
        if self.hovered_item_slot is not None:
            triggered_events.append(TrySwitchItemInInventory(self.hovered_item_slot.slot_number))
            self.item_slot_being_dragged = None
        return triggered_events

    def handle_mouse_click(self, player_state: PlayerState) -> List[EventTriggeredFromUi]:
        mouse_click_event = self.ui_view.handle_mouse_click()
        triggered_events: List[EventTriggeredFromUi] = []
        if mouse_click_event:
            if mouse_click_event == mouse_click_event.TOGGLE_SOUND:
                triggered_events.append(ToggleSound())
            elif mouse_click_event == mouse_click_event.SAVE:
                triggered_events.append(SaveGame())

        if self.hovered_item_slot and self.hovered_item_slot.item_type:
            self.item_slot_being_dragged = self.hovered_item_slot
            triggered_events.append(StartDraggingItemOrConsumable())
        if self.hovered_consumable_slot and self.hovered_consumable_slot.consumable_types:
            self.consumable_slot_being_dragged = self.hovered_consumable_slot
            triggered_events.append(StartDraggingItemOrConsumable())
        if self.hovered_talent_choice_option:
            choice_index, option_index = self.hovered_talent_choice_option
            # TODO Don't depend on player state for this
            if len(player_state.chosen_talent_option_indices) == choice_index:
                triggered_events.append(PickTalent(option_index))
        return triggered_events

    def handle_mouse_release(self, game_state: GameState):
        triggered_events = []
        if self.item_slot_being_dragged:
            if self.hovered_item_slot and self.item_slot_being_dragged.slot_number != self.hovered_item_slot.slot_number:
                triggered_events.append(DragItemBetweenInventorySlots(
                    self.item_slot_being_dragged.slot_number, self.hovered_item_slot.slot_number))
            if not self.is_mouse_over_ui:
                event = DropItemOnGround(
                    self.item_slot_being_dragged.slot_number,
                    get_mouse_world_pos(game_state, self.mouse_screen_position))
                triggered_events.append(event)
            self.item_slot_being_dragged = None

        if self.consumable_slot_being_dragged:
            if self.hovered_consumable_slot and self.consumable_slot_being_dragged.slot_number != self.hovered_consumable_slot.slot_number:
                event = DragConsumableBetweenInventorySlots(
                    self.consumable_slot_being_dragged.slot_number, self.hovered_consumable_slot.slot_number)
                triggered_events.append(event)
            if not self.is_mouse_over_ui:
                event = DropConsumableOnGround(
                    self.consumable_slot_being_dragged.slot_number,
                    get_mouse_world_pos(game_state, self.mouse_screen_position))
                triggered_events.append(event)
            self.consumable_slot_being_dragged = None

        return triggered_events

    def change_dialog_option(self, delta: int):
        self.dialog.option_index = (self.dialog.option_index + delta) % len(self.dialog.data.options)
        self.ui_view.update_dialog(DialogConfig(self.dialog.data, self.dialog.option_index))

    def start_dialog_with_npc(self, npc: NonPlayerCharacter):
        self.dialog.active = True
        self.dialog.npc = npc
        self.dialog.data = get_dialog_data(npc.npc_type)
        if self.dialog.option_index >= len(self.dialog.data.options):
            self.dialog.option_index = 0
        self.ui_view.update_dialog(DialogConfig(self.dialog.data, self.dialog.option_index))

    def has_open_dialog(self) -> bool:
        return self.dialog.active

    def handle_space_click(self) -> Optional[Tuple[NonPlayerCharacter, int]]:
        if self.dialog.active:
            self.dialog.active = False
            self.ui_view.update_dialog(None)
            return self.dialog.npc, self.dialog.option_index
        return None
