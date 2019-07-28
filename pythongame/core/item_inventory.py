from enum import Enum
from typing import Optional, List, Any

from pythongame.core.common import ItemType


class ItemEquipmentCategory(Enum):
    CHEST = 1
    MAIN_HAND = 2
    OFF_HAND = 3
    HEAD = 4
    NECK = 5
    RING = 6


class ItemInSlot:
    def __init__(self, item_effect, item_equipment_category: ItemEquipmentCategory):
        self.item_effect = item_effect
        self.item_equipment_category = item_equipment_category


class ItemInventorySlot:
    def __init__(self, item: Optional[ItemInSlot], enforced_equipment_category: Optional[ItemEquipmentCategory]):
        self.item = item
        # TODO
        # items should only give bonuses if they are equipped into the appropriate inventory slot
        # example: you should not benefit from having multiple helmets in your inventory
        self.enforced_equipment_category = enforced_equipment_category

    def is_empty(self) -> bool:
        return self.item is None

    def allows_item(self, item: ItemInSlot):
        if not self.enforced_equipment_category or not item:
            return True
        return item.item_equipment_category == self.enforced_equipment_category


class ItemInventory:
    def __init__(self, slots: List[ItemInventorySlot]):
        self.slots = slots

    def switch_item_slots(self, slot_1_index: int, slot_2_index: int) -> bool:
        slot_1 = self.slots[slot_1_index]
        slot_2 = self.slots[slot_2_index]
        content_1 = slot_1.item
        content_2 = slot_2.item
        if slot_2.allows_item(content_1) and slot_1.allows_item(content_2):
            slot_1.item = content_2
            slot_2.item = content_1
            return True
        return False

    def has_item_in_inventory(self, item_type: ItemType):
        matches = [slot for slot in self.slots
                   if slot.item and slot.item.item_effect.get_item_type() == item_type]
        if len(matches) > 0:
            return True

    def lose_item_from_inventory(self, item_type: ItemType):
        for slot_number in range(len(self.slots)):
            slot = self.slots[slot_number]
            if slot.item.item_effect and slot.item.item_effect.get_item_type() == item_type:
                self.slots[slot_number].item = None
                return
        print("WARN: item not found in inventory: " + item_type.name)

    def _find_empty_slot_for_item(self, item: ItemInSlot) -> Optional[int]:
        empty_slots = [slot for slot in range(len(self.slots))
                       if self.slots[slot].is_empty() and self.slots[slot].allows_item(item)]
        if empty_slots:
            return empty_slots[0]
        return None

    def is_slot_empty(self, slot_index: int) -> bool:
        return self.slots[slot_index].is_empty()

    def try_add_item(self, item_effect, item_equipment_category: ItemEquipmentCategory):
        item_in_slot = ItemInSlot(item_effect, item_equipment_category)
        empty_slot = self._find_empty_slot_for_item(item_in_slot)
        if empty_slot is not None:
            self.slots[empty_slot].item = item_in_slot
            return True
        return False

    def get_item_type_in_slot(self, slot_index: int) -> ItemType:
        if self.slots[slot_index].is_empty():
            raise Exception("Can't get item type from empty inventory slot: " + str(slot_index))
        return self.slots[slot_index].item.item_effect.get_item_type()

    def remove_item_from_slot(self, slot_index: int) -> ItemType:
        if self.slots[slot_index].is_empty():
            raise Exception("Can't remove item from empty inventory slot: " + str(slot_index))
        item_type = self.slots[slot_index].item.item_effect.get_item_type()
        self.slots[slot_index].item = None
        return item_type

    def get_all_item_effects(self) -> List[Any]:
        return [slot.item.item_effect for slot in self.slots if slot.item is not None]
