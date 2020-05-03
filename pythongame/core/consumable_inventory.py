from typing import Dict, List, Optional

from pythongame.core.common import ConsumableType, Observable


class ConsumableInventory:
    def __init__(self, slots: Dict[int, List[ConsumableType]]):
        self.consumables_in_slots: Dict[int, List[ConsumableType]] = slots
        self.capacity_per_slot = 2
        self.was_updated = Observable()

    def set_slots(self, slots: Dict[int, List[ConsumableType]]):
        self.consumables_in_slots = slots
        self.notify_observers()

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
            self.notify_observers()
            return
        empty_slots = [consumables for consumables in self.consumables_in_slots.values() if len(consumables) == 0]
        if empty_slots:
            empty_slots[0].append(consumable_type)
            self.notify_observers()
            return
        for consumables in self.consumables_in_slots.values():
            if len(consumables) < self.capacity_per_slot:
                consumables.append(consumable_type)
                self.notify_observers()
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
        self.notify_observers()

    def remove_consumable_from_slot(self, slot_number: int) -> Optional[ConsumableType]:
        if self.consumables_in_slots[slot_number]:
            removed = self.consumables_in_slots[slot_number].pop(0)
            self.notify_observers()
            return removed
        return None

    def get_consumable_at_slot(self, slot_number: int) -> Optional[ConsumableType]:
        return self.consumables_in_slots[slot_number][0] if len(self.consumables_in_slots[slot_number]) > 0 else None

    def notify_observers(self):
        self.was_updated.notify(self.consumables_in_slots)
