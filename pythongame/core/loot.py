import math
import random
from typing import Optional, List, Dict

from pythongame.core.common import ConsumableType, ItemType


# Represents the smallest unit of loot. It shows up on the ground as "one item"
class LootEntry:
    def __init__(self, money_amount: Optional[int], item_type: Optional[ItemType],
                 consumable_type: Optional[ConsumableType]):
        self.money_amount = money_amount
        self.item_type = item_type
        self.consumable_type = consumable_type

    def is_item(self) -> bool:
        return self.item_type is not None

    @staticmethod
    def money(amount: int):
        return LootEntry(amount, None, None)

    @staticmethod
    def item(item_type: ItemType):
        return LootEntry(None, item_type, None)

    @staticmethod
    def consumable(consumable_type: ConsumableType):
        return LootEntry(None, None, consumable_type)


# A group of possible loot entries that are interdependent.
# Example: 40% to find the group {A, B, C} and exactly 2 entries of the group will be dropped
class LootGroup:
    def __init__(self, pick_n: int, entries: List[LootEntry], chance_to_get_group: float):
        self.pick_n = pick_n
        self.entries = entries
        self.chance_to_get_group = chance_to_get_group

    @staticmethod
    def single(single_entry: LootEntry, chance_to_get_entry: float):
        return LootGroup(1, [single_entry], chance_to_get_entry)


class LootTable:
    def generate_loot(self) -> List[LootEntry]:
        raise Exception("Sub-classes must override this method!")


# Represents the loot of one enemy. Made up of one to many "loot groups"
class StaticLootTable(LootTable):
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
        return StaticLootTable([LootGroup.single(single_entry, chance_to_get_entry)])


class LeveledLootTable(LootTable):
    def __init__(self, chance_to_drop_anything: float, level: int, entries_by_level: Dict[int, List[ItemType]]):
        self.chance_to_drop_anything = chance_to_drop_anything
        self.level = level
        if [entries for entries in entries_by_level.values() if len(entries) == 0]:
            raise Exception("Invalid loot table! Some level doesn't have any items: %s" % entries_by_level)
        self.entries_by_level = entries_by_level
        self.levels = list(entries_by_level.keys())
        self.level_weights = [1.0 / math.pow(2, abs(level - self.level)) for level in self.levels]

    def generate_loot(self) -> List[LootEntry]:
        if random.random() >= self.chance_to_drop_anything:
            return []
        level = random.choices(self.levels, weights=self.level_weights)[0]

        item_type = random.choice(self.entries_by_level[level])

        return [LootEntry.item(item_type)]
