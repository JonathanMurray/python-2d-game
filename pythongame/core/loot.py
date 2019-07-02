import random
from typing import Optional, List

from pythongame.core.common import ConsumableType, ItemType


class LootEntry:
    def __init__(self, money_amount: Optional[int], item_type: Optional[ItemType],
                 consumable_type: Optional[ConsumableType]):
        self.money_amount = money_amount
        self.item_type = item_type
        self.consumable_type = consumable_type

    @staticmethod
    def money(amount: int):
        return LootEntry(amount, None, None)

    @staticmethod
    def item(item_type: ItemType):
        return LootEntry(None, item_type, None)

    @staticmethod
    def consumable(consumable_type: ConsumableType):
        return LootEntry(None, None, consumable_type)


class LootGroup:
    def __init__(self, pick_n: int, entries: List[LootEntry], chance_to_get_group: float):
        self.pick_n = pick_n
        self.entries = entries
        self.chance_to_get_group = chance_to_get_group

    @staticmethod
    def single(single_entry: LootEntry, chance_to_get_entry: float):
        return LootGroup(1, [single_entry], chance_to_get_entry)


class LootTable:
    def __init__(self, groups: List[LootGroup]):
        self.groups = groups

    def generate_loot(self) -> List[LootEntry]:
        loot: List[LootEntry] = []
        for group in self.groups:
            if random.random() < group.chance_to_get_group:
                entries = list(group.entries)
                for i in range(group.pick_n):
                    pick_i = random.choice(entries)
                    loot.append(pick_i)
                    entries.remove(pick_i)
        return loot

    @staticmethod
    def single(single_entry: LootEntry, chance_to_get_entry: float):
        return LootTable([LootGroup.single(single_entry, chance_to_get_entry)])
