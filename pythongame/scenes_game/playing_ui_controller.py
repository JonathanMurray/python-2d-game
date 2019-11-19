from typing import Optional, Tuple, List

from pythongame.core.game_state import GameState
from pythongame.core.npc_behaviors import DialogGraphics
from pythongame.core.talents import talents_graphics_from_state
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, MouseHoverEvent


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


class PlayingUiController:

    def __init__(
            self,
            ui_view: GameUiView,
            ui_state: GameUiState):
        self.game_ui_view = ui_view
        self.ui_state = ui_state
        self.item_slot_being_dragged: Optional[int] = None
        self.consumable_slot_being_dragged: Optional[int] = None

    def render_and_handle_mouse(
            self, game_state: GameState, text_in_topleft_corner: str, dialog_graphics: DialogGraphics,
            mouse_screen_position: Tuple[int, int], mouse_was_just_clicked: bool,
            mouse_was_just_released: bool, right_mouse_was_just_clicked: bool) -> List[EventTriggeredFromUi]:

        triggered_events: List[EventTriggeredFromUi] = []

        # TODO If dragging an item, highlight the inventory slots that are valid for the item?

        talents_graphics = talents_graphics_from_state(
            game_state.player_state.talents_state, game_state.player_state.level,
            game_state.player_state.chosen_talent_option_indices)

        mouse_hover_event: MouseHoverEvent = self.game_ui_view.render_ui(
            player_state=game_state.player_state,
            ui_state=self.ui_state,
            player_speed_multiplier=game_state.player_entity.get_speed_multiplier(),
            text_in_topleft_corner=text_in_topleft_corner,
            is_paused=False,
            mouse_screen_position=mouse_screen_position,
            dialog=dialog_graphics,
            talents=talents_graphics)

        # DRAGGING ITEMS

        hovered_item_slot_number = mouse_hover_event.item_slot_number

        if mouse_was_just_clicked and hovered_item_slot_number is not None:
            if not game_state.player_state.item_inventory.is_slot_empty(hovered_item_slot_number):
                self.item_slot_being_dragged = hovered_item_slot_number
                triggered_events.append(StartDraggingItemOrConsumable())
        if right_mouse_was_just_clicked and hovered_item_slot_number is not None:
            triggered_events.append(TrySwitchItemInInventory(hovered_item_slot_number))

        if self.item_slot_being_dragged is not None:
            item_type = game_state.player_state.item_inventory.get_item_type_in_slot(self.item_slot_being_dragged)
            self.game_ui_view.render_item_being_dragged(item_type, mouse_screen_position)

        if mouse_was_just_released and self.item_slot_being_dragged is not None:
            if hovered_item_slot_number is not None and self.item_slot_being_dragged != hovered_item_slot_number:
                triggered_events.append(DragItemBetweenInventorySlots(
                    self.item_slot_being_dragged, hovered_item_slot_number))
            if not mouse_hover_event.is_over_ui:
                event = DropItemOnGround(
                    self.item_slot_being_dragged, get_mouse_world_pos(game_state, mouse_screen_position))
                triggered_events.append(event)
            self.item_slot_being_dragged = None

        # DRAGGING CONSUMABLES

        hovered_consumable_slot_number = mouse_hover_event.consumable_slot_number

        if mouse_was_just_clicked and hovered_consumable_slot_number is not None:
            if game_state.player_state.consumable_inventory.consumables_in_slots[hovered_consumable_slot_number]:
                self.consumable_slot_being_dragged = hovered_consumable_slot_number
                triggered_events.append(StartDraggingItemOrConsumable())

        if self.consumable_slot_being_dragged is not None:
            consumable_type = game_state.player_state.consumable_inventory.consumables_in_slots[
                self.consumable_slot_being_dragged][0]
            self.game_ui_view.render_consumable_being_dragged(consumable_type, mouse_screen_position)

        if mouse_was_just_released and self.consumable_slot_being_dragged is not None:
            if hovered_consumable_slot_number is not None and self.consumable_slot_being_dragged != hovered_consumable_slot_number:
                event = DragConsumableBetweenInventorySlots(
                    self.consumable_slot_being_dragged, hovered_consumable_slot_number)
                triggered_events.append(event)
            if not mouse_hover_event.is_over_ui:
                event = DropConsumableOnGround(
                    self.consumable_slot_being_dragged, get_mouse_world_pos(game_state, mouse_screen_position))
                triggered_events.append(event)
            self.consumable_slot_being_dragged = None

        # UI TOGGLES

        if mouse_was_just_clicked and mouse_hover_event.ui_toggle is not None:
            self.ui_state.notify_toggle_was_clicked(mouse_hover_event.ui_toggle)
            triggered_events.append(ClickUiToggle())

        # PICKING TALENTS

        if mouse_was_just_clicked and mouse_hover_event.talent_choice_option is not None:
            choice_index, option_index = mouse_hover_event.talent_choice_option
            if len(game_state.player_state.chosen_talent_option_indices) == choice_index:
                triggered_events.append(PickTalent(option_index))

        return triggered_events
