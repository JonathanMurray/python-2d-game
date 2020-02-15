from typing import Dict, List

from pythongame.core.common import ItemType, LootTableId, ConsumableType
from pythongame.core.game_data import get_consumables_with_level
from pythongame.core.item_data import get_items_with_level, get_items_within_levels
from pythongame.core.loot import LootEntry, LeveledLootTable, StaticLootTable, LootGroup, LootTable

loot_tables: Dict[LootTableId, LootTable] = {}


def get_loot_table(loot_table_id: LootTableId) -> LootTable:
    return loot_tables[loot_table_id]


def register_loot_tables():
    loot_tables[LootTableId.LEVEL_1] = _table_for_monster_level(1)
    loot_tables[LootTableId.LEVEL_2] = _table_for_monster_level(2)
    loot_tables[LootTableId.LEVEL_3] = _table_for_monster_level(3)
    loot_tables[LootTableId.LEVEL_4] = _table_for_monster_level(4)
    loot_tables[LootTableId.LEVEL_5] = _table_for_monster_level(5)
    loot_tables[LootTableId.LEVEL_6] = _table_for_monster_level(6)
    loot_tables[LootTableId.LEVEL_7] = _table_for_monster_level(7)
    loot_tables[LootTableId.CHEST] = LeveledLootTable(
        item_drop_chance=1,
        level=3,
        item_types_by_level=_item_types_for_monster_level(3),
        consumable_types_by_level=_consumable_types_for_monster_level(3),
        consumable_drop_chance=0)
    loot_tables[LootTableId.BOSS_GOBLIN] = _table_for_goblin_boss()
    loot_tables[LootTableId.BOSS_WARRIOR_KING] = _table_for_human_boss()


def _table_for_goblin_boss() -> LootTable:
    return StaticLootTable(
        [
            LootGroup(2, [LootEntry.item(ItemType.FROG), LootEntry.consumable(ConsumableType.WARP_STONE)], 1),
            LootGroup(1, [LootEntry.item(item_type) for item_type in get_items_within_levels(5, 10)], 1),
            LootGroup(1, [LootEntry.money(2), LootEntry.money(3), LootEntry.money(5)], 0.7)
        ]
    )


def _table_for_human_boss() -> LootTable:
    return StaticLootTable(
        [
            LootGroup.single(LootEntry.consumable(ConsumableType.WARP_STONE), 1),
            LootGroup(1, [LootEntry.item(item_type) for item_type in get_items_within_levels(5, 10)], 1),
            LootGroup.single(LootEntry.item(ItemType.KEY), 1),
        ]
    )


def _table_for_monster_level(monster_level: int) -> LootTable:
    return LeveledLootTable(
        item_drop_chance=0.15,
        level=monster_level,
        item_types_by_level=_item_types_for_monster_level(monster_level),
        consumable_types_by_level=_consumable_types_for_monster_level(monster_level),
        consumable_drop_chance=0.05)


def _item_types_for_monster_level(monster_level: int) -> Dict[int, List[ItemType]]:
    d = {}

    for level in range(max(monster_level - 3, 1), monster_level + 3):
        items = get_items_with_level(level)
        if items:
            d[level] = items
    return d


def _consumable_types_for_monster_level(monster_level: int) -> Dict[int, List[ConsumableType]]:
    d = {}

    for level in range(max(monster_level - 3, 1), monster_level + 3):
        consumables = get_consumables_with_level(level)
        if consumables:
            d[level] = consumables
    return d
