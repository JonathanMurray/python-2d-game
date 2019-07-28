from typing import Dict, List, Optional

from pythongame.core.common import ConsumableType


class ConsumableInventory:
    def __init__(self, slots: Dict[int, ConsumableType]):
        self.consumables_in_slots: Dict[int, List[ConsumableType]] = {}
        self.capacity_per_slot = 2
        for slot_number in slots:
            self.consumables_in_slots[slot_number] = []
            if slots[slot_number]:
                self.consumables_in_slots[slot_number].append(slots[slot_number])

    def has_space_for_more(self) -> bool:
        slots_with_space = [consumables for consumables in self.consumables_in_slots.values() if
                            len(consumables) < self.capacity_per_slot]
        return len(slots_with_space) > 0

    def add_consumable(self, consumable_type: ConsumableType):
        non_full_slots_with_same_type = [consumables for consumables in self.consumables_in_slots.values()
                                         if 0 < len(consumables) < self.capacity_per_slot
                                         and consumables[0] == consumable_type]
        if non_full_slots_with_same_type:
            non_full_slots_with_same_type[0].append(consumable_type)
            return
        empty_slots = [consumables for consumables in self.consumables_in_slots.values() if len(consumables) == 0]
        if empty_slots:
            empty_slots[0].append(consumable_type)
            return
        for consumables in self.consumables_in_slots.values():
            if len(consumables) < self.capacity_per_slot:
                consumables.append(consumable_type)
                return
        raise Exception("No space for consumable!")

    def drag_consumable_between_inventory_slots(self, from_slot: int, to_slot: int):
        consumable_type_1 = self.remove_consumable_from_slot(from_slot)
        if len(self.consumables_in_slots[to_slot]) < self.capacity_per_slot:
            self.consumables_in_slots[to_slot].insert(0, consumable_type_1)
        else:
            consumable_type_2 = self.remove_consumable_from_slot(to_slot)
            self.consumables_in_slots[to_slot].insert(0, consumable_type_1)
            self.consumables_in_slots[from_slot].insert(0, consumable_type_2)

    def remove_consumable_from_slot(self, slot_number: int) -> Optional[ConsumableType]:
        if self.consumables_in_slots[slot_number]:
            return self.consumables_in_slots[slot_number].pop(0)
        else:
            return None

    def get_consumable_at_slot(self, slot_number: int) -> Optional[ConsumableType]:
        return self.consumables_in_slots[slot_number][0] if len(self.consumables_in_slots[slot_number]) > 0 else None
