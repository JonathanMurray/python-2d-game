import math
import random
from typing import List, Dict

from pythongame.core.common import ConsumableType, ItemType, ItemId
# Represents the smallest unit of loot. It shows up on the ground as "one item"
from pythongame.core.item_data import random_item_two_affixes, random_item_one_affix, get_item_data_by_type
from pythongame.core.item_inventory import ItemEquipmentCategory


class LootEntry:
    pass


class MoneyLootEntry(LootEntry):
    def __init__(self, amount: int):
        self.amount = amount


class ConsumableLootEntry(LootEntry):
    def __init__(self, consumable_type: ConsumableType):
        self.consumable_type = consumable_type


class ItemLootEntry(LootEntry):
    def __init__(self, item_type: ItemType):
        self.item_type = item_type


class AffixedItemLootEntry(LootEntry):
    def __init__(self, item_id: ItemId):
        self.item_id = item_id


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
    def generate_loot(self, increased_money_chance: float, increased_rare_or_unique_chance: float,
                      is_inside_dungeon: bool) -> List[LootEntry]:
        raise Exception("Sub-classes must override this method!")


class LeveledLootTable(LootTable):
    def __init__(self,
                 guaranteed_drops: List[LootEntry],
                 item_drop_chance: float,
                 item_rare_or_unique_chance: float,
                 level: int,
                 regular_item_types_by_level: Dict[int, List[ItemType]],
                 unique_item_types_by_level: Dict[int, List[ItemType]],
                 consumable_drop_chance: float,
                 consumable_types_by_level: Dict[int, List[ConsumableType]]):
        self.guaranteed_drops = guaranteed_drops
        self.item_drop_chance = item_drop_chance
        self.item_rare_or_unique_chance = item_rare_or_unique_chance
        self.consumable_drop_chance = consumable_drop_chance
        self.level = level
        if [entries for entries in regular_item_types_by_level.values() if len(entries) == 0]:
            raise Exception("Invalid loot table: %s" % regular_item_types_by_level)
        if [entries for entries in unique_item_types_by_level.values() if len(entries) == 0]:
            raise Exception("Invalid loot table: %s" % unique_item_types_by_level)
        self.regular_item_types_by_level = regular_item_types_by_level
        self.unique_item_types_by_level = unique_item_types_by_level
        self.item_levels = list(regular_item_types_by_level.keys())
        self.item_level_weights = [1.0 / math.pow(1.5, abs(level - self.level)) for level in self.item_levels]
        if [entries for entries in consumable_types_by_level.values() if len(entries) == 0]:
            raise Exception("Invalid loot table: %s" % consumable_types_by_level)

        self.consumable_types_by_level = consumable_types_by_level
        self.consumable_levels = list(consumable_types_by_level.keys())
        self.consumable_level_weights = [1.0 / math.pow(1.5, abs(level - self.level)) for level in
                                         self.consumable_levels]

        self.money_drop_chance = 0.15

    def generate_loot(self, increased_money_chance: float, increased_rare_or_unique_chance: float,
                      is_inside_dungeon: bool) -> List[LootEntry]:
        loot = list(self.guaranteed_drops)
        if random.random() <= self.item_drop_chance:
            item_level = random.choices(self.item_levels, weights=self.item_level_weights)[0]
            rare_or_unique = random.random() <= self.item_rare_or_unique_chance * (1 + increased_rare_or_unique_chance)
            # There are 4 classes of items:
            # common: a regular item with no affixes
            # rare-1: a regular item with 1 bonus affix
            # rare-2: a regular item with 2 bonus affixes
            # unique: a unique item
            if rare_or_unique:
                random_outcome = random.random()
                if random_outcome <= 0.25 and item_level in self.unique_item_types_by_level:
                    unique_item_type = random.choice(self.unique_item_types_by_level[item_level])
                    unique_item = ItemLootEntry(unique_item_type)
                    loot.append(unique_item)
                elif random_outcome <= 0.4:
                    rare_item_id = random_item_two_affixes(item_level)
                    rare_item = AffixedItemLootEntry(rare_item_id)
                    loot.append(rare_item)
                else:
                    rare_item_id = random_item_one_affix(item_level)
                    rare_item = AffixedItemLootEntry(rare_item_id)
                    loot.append(rare_item)
            else:
                item_type = random.choice(self.regular_item_types_by_level[item_level])
                common_item = ItemLootEntry(item_type)
                loot.append(common_item)

        if random.random() <= self.consumable_drop_chance:
            # Warp stone doesn't have a level, but should be dropped across all levels
            if random.random() < 0.15:
                consumable_type = ConsumableType.WARP_STONE
            else:
                consumable_level = random.choices(self.consumable_levels, weights=self.consumable_level_weights)[0]
                consumable_type = random.choice(self.consumable_types_by_level[consumable_level])
            loot.append(ConsumableLootEntry(consumable_type))
        if random.random() <= self.money_drop_chance:
            amount = random.randint(1, self.level)
            if random.random() <= increased_money_chance:  # NOTE: anything above 100% "increased chance" is wasted
                amount *= 2
            loot.append(MoneyLootEntry(amount))

        if is_inside_dungeon:
            loot = [entry for entry in loot if _allowed_drop_inside_dungeon(entry)]

        return loot


def _allowed_drop_inside_dungeon(loot_entry: LootEntry):
    if isinstance(loot_entry, ItemLootEntry):
        if get_item_data_by_type(loot_entry.item_type).item_equipment_category == ItemEquipmentCategory.QUEST:
            # Player has probably completed the quest anyway and there may be several bosses inside the dungeon, so the
            # ground can get quite crowded
            return False
    if isinstance(loot_entry, ConsumableLootEntry):
        if loot_entry.consumable_type == ConsumableType.WARP_STONE:
            # Warp stones can't be used inside dungeons, and bosses are guaranteed to drop them
            return False
    return True
