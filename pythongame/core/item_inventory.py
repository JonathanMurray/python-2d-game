from enum import Enum
from typing import Optional, List, Any

from pythongame.core.common import Observable, ItemId


class ItemEquipmentCategory(Enum):
    CHEST = 1
    MAIN_HAND = 2
    OFF_HAND = 3
    HEAD = 4
    NECK = 5
    RING = 6
    QUEST = 10


ITEM_EQUIPMENT_CATEGORY_NAMES = {
    ItemEquipmentCategory.CHEST: "Chest",
    ItemEquipmentCategory.MAIN_HAND: "Main-Hand",
    ItemEquipmentCategory.OFF_HAND: "Off-Hand",
    ItemEquipmentCategory.HEAD: "Head",
    ItemEquipmentCategory.NECK: "Neck",
    ItemEquipmentCategory.RING: "Ring",
    ItemEquipmentCategory.QUEST: "Quest"
}


class ItemActivationEvent:
    item_id: ItemId
    pass


class ItemWasActivated(ItemActivationEvent):
    def __init__(self, item_id: ItemId):
        self.item_id = item_id


class ItemWasDeactivated(ItemActivationEvent):
    def __init__(self, item_id: ItemId):
        self.item_id = item_id


class ItemActivationStateDidNotChange(ItemActivationEvent):
    def __init__(self, item_id: ItemId):
        self.item_id = item_id


class ItemInSlot:
    def __init__(self, item_id: ItemId, item_effect, item_equipment_category: ItemEquipmentCategory):
        self.item_id = item_id
        self.item_effect = item_effect
        self.item_equipment_category = item_equipment_category

    def __repr__(self):
        return str(self.item_effect)


class ItemInventorySlot:
    def __init__(self, item: Optional[ItemInSlot], enforced_equipment_category: Optional[ItemEquipmentCategory]):
        self.item = item
        self.enforced_equipment_category = enforced_equipment_category

    def is_empty(self) -> bool:
        return self.item is None

    def can_contain_item(self, item: Optional[ItemInSlot]):
        if not self.enforced_equipment_category or not item:
            return True
        return item.item_equipment_category == self.enforced_equipment_category

    # Putting an item in an 'active' inventory slot enables the effect of that item.
    # Moving it to a slot that is not 'active', removes the effect
    # Slots that are not 'active' simply serve as storage
    def is_active(self) -> bool:
        return self.enforced_equipment_category is not None

    def get_item_id(self) -> ItemId:
        return self.item.item_id

    def __repr__(self):
        return str(self.item)


class ItemInventory:
    def __init__(self, slots: List[ItemInventorySlot]):
        self.slots = slots
        self.was_updated = Observable()

    def switch_item_slots(self, slot_1_index: int, slot_2_index: int) -> List[ItemActivationEvent]:
        slot_1 = self.slots[slot_1_index]
        slot_2 = self.slots[slot_2_index]
        content_1 = slot_1.item
        content_2 = slot_2.item
        events = []
        is_switch_allowed = slot_2.can_contain_item(content_1) and slot_1.can_contain_item(content_2)
        if is_switch_allowed:
            if content_1:
                item_id_1 = slot_1.get_item_id()
                if slot_1.is_active() and not slot_2.is_active():
                    event_1 = ItemWasDeactivated(item_id_1)
                elif not slot_1.is_active() and slot_2.is_active():
                    event_1 = ItemWasActivated(item_id_1)
                else:
                    event_1 = ItemActivationStateDidNotChange(item_id_1)
                events.append(event_1)
            if content_2:
                item_id_2 = slot_2.get_item_id()
                if slot_2.is_active() and not slot_1.is_active():
                    event_2 = ItemWasDeactivated(item_id_2)
                elif not slot_2.is_active() and slot_1.is_active():
                    event_2 = ItemWasActivated(item_id_2)
                else:
                    event_2 = ItemActivationStateDidNotChange(item_id_2)
                events.append(event_2)
            slot_1.item = content_2
            slot_2.item = content_1

        if len(events) == 2:
            # If switching two items that both have active abilities, the currently active ability needs to be removed
            # before the new one can be activated. If we don't switch the order here, the consequence is that no ability
            # will be active.
            if isinstance(events[0], ItemWasActivated) and isinstance(events[1], ItemWasDeactivated):
                events = [events[1], events[0]]

        self.notify_observers()
        return events

    def try_switch_item_at_slot(self, slot_index: int) -> List[ItemActivationEvent]:
        if self.slots[slot_index].is_empty():
            return []
        for other_slot_index in [s for s in range(len(self.slots)) if s != slot_index]:
            events = self.switch_item_slots(slot_index, other_slot_index)
            if events:
                self.notify_observers()
                return events
        return []

    def has_item_in_inventory(self, item_id: ItemId):
        matches = [slot for slot in self.slots if not slot.is_empty() and slot.get_item_id() == item_id]
        if len(matches) > 0:
            return True

    def lose_item_from_inventory(self, item_id: ItemId):
        for slot_number in range(len(self.slots)):
            slot = self.slots[slot_number]
            if not slot.is_empty() and slot.get_item_id() == item_id:
                self.slots[slot_number].item = None
                self.notify_observers()
                return
        print("WARN: item not found in inventory: " + str(item_id))

    # Note: this will need to return events, if it's used for items that have effects
    def is_slot_empty(self, slot_index: int) -> bool:
        return self.slots[slot_index].is_empty()

    def try_add_item(self, item_id: ItemId, item_effect, item_equipment_category: ItemEquipmentCategory) \
            -> Optional[ItemActivationEvent]:
        item_in_slot = ItemInSlot(item_id, item_effect, item_equipment_category)
        empty_slot_index = self._find_empty_slot_for_item(item_in_slot)
        if empty_slot_index is not None:
            slot = self.slots[empty_slot_index]
            slot.item = item_in_slot
            self.notify_observers()
            if slot.is_active():
                return ItemWasActivated(item_id)
            else:
                return ItemActivationStateDidNotChange(item_id)
        return None

    def put_item_in_inventory_slot(self, item_id: ItemId, item_effect, item_equipment_category: ItemEquipmentCategory,
                                   slot_number: int) -> ItemActivationEvent:
        item_in_slot = ItemInSlot(item_id, item_effect, item_equipment_category)
        slot = self.slots[slot_number]
        if not slot.is_empty():
            raise Exception("Can't put item in non-empty slot!")
        slot.item = item_in_slot
        self.notify_observers()
        if slot.is_active():
            return ItemWasActivated(item_id)
        else:
            return ItemActivationStateDidNotChange(item_id)

    def _find_empty_slot_for_item(self, item: ItemInSlot) -> Optional[int]:
        empty_slot_indices = [i for i in range(len(self.slots))
                              if self.slots[i].is_empty() and self.slots[i].can_contain_item(item)]
        if empty_slot_indices:
            return empty_slot_indices[0]
        return None

    def remove_item_from_slot(self, slot_index: int) -> ItemActivationEvent:
        slot = self.slots[slot_index]
        if slot.is_empty():
            raise Exception("Can't remove item from empty inventory slot: " + str(slot_index))
        item_id = slot.get_item_id()
        slot.item = None
        self.notify_observers()
        if slot.is_active():
            return ItemWasDeactivated(item_id)
        return ItemActivationStateDidNotChange(item_id)

    def clear(self) -> List[ItemActivationEvent]:
        events = []
        for slot in self.slots:
            if not slot.is_empty() and slot.is_active():
                active_item_id = slot.get_item_id()
                events.append(ItemWasDeactivated(active_item_id))
            slot.item = None
        self.notify_observers()
        return events

    def get_all_active_item_effects(self) -> List[Any]:
        return [slot.item.item_effect for slot in self.slots if slot.is_active() and not slot.is_empty()]

    def notify_observers(self):
        self.was_updated.notify(self.slots)

    def __repr__(self):
        return str(self.slots)
