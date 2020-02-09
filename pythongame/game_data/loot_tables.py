from typing import Dict

from pythongame.core.common import ItemType, LootTableId, ConsumableType
from pythongame.core.game_data import get_items_with_level
from pythongame.core.loot import LootEntry, LeveledLootTable, StaticLootTable, LootGroup, LootTable

# TODO remove these hard-coded loot item groups
LOOT_ITEMS_3 = [
    LootEntry.item(ItemType.MESSENGERS_HAT),
    LootEntry.item(ItemType.SKULL_STAFF),
    LootEntry.item(ItemType.ROD_OF_LIGHTNING),
    LootEntry.item(ItemType.ZULS_AEGIS),
    LootEntry.item(ItemType.SKULL_SHIELD),
    LootEntry.item(ItemType.GOATS_RING),
    LootEntry.item(ItemType.BLOOD_AMULET),
    LootEntry.item(ItemType.STONE_AMULET),
    LootEntry.item(ItemType.KNIGHTS_ARMOR),
    LootEntry.item(ItemType.RING_OF_POWER),
    LootEntry.item(ItemType.ROYAL_SWORD),
    LootEntry.item(ItemType.ROYAL_DAGGER),
    LootEntry.item(ItemType.FIRE_WAND),
    LootEntry.item(ItemType.ELITE_HELMET),
    LootEntry.item(ItemType.DRUIDS_RING),
    LootEntry.item(ItemType.HEALING_WAND),
    LootEntry.item(ItemType.ELVEN_ARMOR),
    LootEntry.item(ItemType.WHIP),
    LootEntry.item(ItemType.SERPENT_SWORD),
    LootEntry.item(ItemType.SORCERESS_ROBE)
]

# TODO remove these hard-coded loot item groups
LOOT_ITEMS_4 = [
    LootEntry.item(ItemType.BLESSED_CHALICE),  # 5
    LootEntry.item(ItemType.WINGED_HELMET),  # 7
    LootEntry.item(ItemType.WARLORDS_ARMOR),  # 7
    LootEntry.item(ItemType.ELITE_ARMOR),  # 5
    LootEntry.item(ItemType.GLADIATOR_ARMOR),  # 6
    LootEntry.item(ItemType.FREEZING_GAUNTLET),  # 6
    LootEntry.item(ItemType.WIZARDS_COWL),  # 5
    LootEntry.item(ItemType.WARLOCKS_COWL),  # 5
    LootEntry.item(ItemType.NOBLE_DEFENDER),  # 6
    LootEntry.item(ItemType.LICH_ARMOR),  # 7
    LootEntry.item(ItemType.MOLTEN_AXE),  # 7
    LootEntry.item(ItemType.CLEAVER),  # 7
    LootEntry.item(ItemType.DESERT_BLADE),  # 7
    LootEntry.item(ItemType.NECKLACE_OF_SUFFERING)  # 6
]

loot_tables: Dict[LootTableId, LootTable] = {}


def register_loot_tables():
    loot_tables[LootTableId.LEVEL_1] = _table_for_monster_level(1)
    loot_tables[LootTableId.LEVEL_2] = _table_for_monster_level(2)
    loot_tables[LootTableId.LEVEL_3] = _table_for_monster_level(3)
    loot_tables[LootTableId.LEVEL_4] = _table_for_monster_level(4)
    loot_tables[LootTableId.LEVEL_5] = _table_for_monster_level(5)
    loot_tables[LootTableId.LEVEL_6] = _table_for_monster_level(6)
    loot_tables[LootTableId.LEVEL_7] = _table_for_monster_level(7)
    loot_tables[LootTableId.CHEST] = LeveledLootTable(chance_to_drop_anything=1, level=3,
                                                      entries_by_level=_entries_for_monster_level(3))
    loot_tables[LootTableId.BOSS_GOBLIN] = _table_for_goblin_boss()
    loot_tables[LootTableId.BOSS_WARRIOR_KING] = _table_for_human_boss()


def _table_for_goblin_boss() -> LootTable:
    return StaticLootTable(
        [
            LootGroup(2, [LootEntry.item(ItemType.FROG), LootEntry.consumable(ConsumableType.WARP_STONE)], 1),
            LootGroup(1, LOOT_ITEMS_3 + LOOT_ITEMS_4, 1),
            LootGroup(1, [LootEntry.money(2), LootEntry.money(3), LootEntry.money(5)], 0.7)
        ]
    )


def _table_for_human_boss() -> LootTable:
    return StaticLootTable(
        [
            LootGroup.single(LootEntry.consumable(ConsumableType.WARP_STONE), 1),
            LootGroup(1, LOOT_ITEMS_4, 1),
            LootGroup.single(LootEntry.item(ItemType.KEY), 1),
        ]
    )


def get_loot_table(loot_table_id: LootTableId) -> LootTable:
    return loot_tables[loot_table_id]


def _table_for_monster_level(monster_level: int) -> LootTable:
    return LeveledLootTable(
        chance_to_drop_anything=0.3,
        level=monster_level,
        entries_by_level=_entries_for_monster_level(monster_level))


def _entries_for_monster_level(monster_level: int):
    d = {}

    for level in range(max(monster_level - 3, 1), monster_level + 3):
        items = get_items_with_level(level)
        if items:
            d[level] = items
    return d
