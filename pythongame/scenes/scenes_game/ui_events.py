from typing import Tuple


class EventTriggeredFromUi:
    pass


class DragItemBetweenInventorySlots(EventTriggeredFromUi):
    def __init__(self, from_slot: int, to_slot: int):
        self.from_slot = from_slot
        self.to_slot = to_slot


class DropItemOnGround(EventTriggeredFromUi):
    def __init__(self, from_slot: int, screen_position: Tuple[int, int]):
        self.from_slot = from_slot
        self.screen_position = screen_position


class DragConsumableBetweenInventorySlots(EventTriggeredFromUi):
    def __init__(self, from_slot: int, to_slot: int):
        self.from_slot = from_slot
        self.to_slot = to_slot


class DropConsumableOnGround(EventTriggeredFromUi):
    def __init__(self, from_slot: int, screen_position: Tuple[int, int]):
        self.from_slot = from_slot
        self.screen_position = screen_position


class PickTalent(EventTriggeredFromUi):
    def __init__(self, tier_index: int, option_index: int):
        self.tier_index = tier_index
        self.option_index = option_index


class ToggleSound(EventTriggeredFromUi):
    pass


class SaveGame(EventTriggeredFromUi):
    pass


class ToggleFullscreen(EventTriggeredFromUi):
    pass


class StartDraggingItemOrConsumable(EventTriggeredFromUi):
    pass


class ToggleWindow(EventTriggeredFromUi):
    pass


class TrySwitchItemInInventory(EventTriggeredFromUi):
    def __init__(self, slot: int):
        self.slot = slot
