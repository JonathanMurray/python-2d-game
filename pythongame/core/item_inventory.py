from typing import Dict, List, Optional, Any

from pythongame.core.common import ConsumableType, ItemType


class ItemInventory:
    def __init__(self, item_slots: Dict[int, Any]):
        self.item_slots = item_slots  # Values are of type AbstractItemEffect

    def switch_item_slots(self, slot_1: int, slot_2: int):
        item_type_1 = self.item_slots[slot_1]
        self.item_slots[slot_1] = self.item_slots[slot_2]
        self.item_slots[slot_2] = item_type_1

    def has_item_in_inventory(self, item_type: ItemType):
        matches = [item_effect for item_effect in self.item_slots.values()
                   if item_effect and item_effect.get_item_type() == item_type]
        if len(matches) > 0:
            return True

    def lose_item_from_inventory(self, item_type: ItemType):
        for slot_number in self.item_slots:
            item_in_slot = self.item_slots[slot_number]
            if item_in_slot and item_in_slot.get_item_type() == item_type:
                self.item_slots[slot_number] = None
                return
        print("WARN: item not found in inventory: " + item_type.name)

    def find_first_empty_item_slot(self) -> Optional[int]:
        empty_slots = [slot for slot in self.item_slots if not self.item_slots[slot]]
        if empty_slots:
            return empty_slots[0]
        return None
