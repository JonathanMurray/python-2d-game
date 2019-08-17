from pythongame.core.common import ItemType, ConsumableType
from pythongame.core.loot import LootTable, LootGroup, LootEntry

LOOT_ITEMS_1 = [
    LootEntry.item(ItemType.WOODEN_SHIELD),
    LootEntry.item(ItemType.LEATHER_COWL),
    LootEntry.item(ItemType.LEATHER_ARMOR),
]

LOOT_ITEMS_2 = [
    LootEntry.item(ItemType.AMULET_OF_MANA_1),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_1),
    LootEntry.item(ItemType.ORB_OF_WISDOM_1),
    LootEntry.item(ItemType.ORB_OF_LIFE_1),
    LootEntry.item(ItemType.ROYAL_DAGGER),
    LootEntry.item(ItemType.BLUE_ROBE_1),
    LootEntry.item(ItemType.BLESSED_SHIELD_1),
    LootEntry.item(ItemType.SOLDIERS_HELMET_1),
]

LOOT_ITEMS_3 = [
    LootEntry.item(ItemType.MESSENGERS_HAT),
    LootEntry.item(ItemType.SWORD_OF_LEECHING),
    LootEntry.item(ItemType.ROD_OF_LIGHTNING),
    LootEntry.item(ItemType.AMULET_OF_MANA_2),
    LootEntry.item(ItemType.AMULET_OF_MANA_3),
    LootEntry.item(ItemType.BLESSED_SHIELD_2),
    LootEntry.item(ItemType.BLESSED_SHIELD_3),
    LootEntry.item(ItemType.SOLDIERS_HELMET_2),
    LootEntry.item(ItemType.SOLDIERS_HELMET_3),
    LootEntry.item(ItemType.BLUE_ROBE_2),
    LootEntry.item(ItemType.BLUE_ROBE_3),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_2),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_3),
    LootEntry.item(ItemType.ORB_OF_WISDOM_2),
    LootEntry.item(ItemType.ORB_OF_WISDOM_3),
    LootEntry.item(ItemType.ORB_OF_LIFE_2),
    LootEntry.item(ItemType.ORB_OF_LIFE_3),
    LootEntry.item(ItemType.ZULS_AEGIS),
    LootEntry.item(ItemType.GOATS_RING),
    LootEntry.item(ItemType.BLOOD_AMULET),
    LootEntry.item(ItemType.KNIGHTS_ARMOR),
    LootEntry.item(ItemType.RING_OF_POWER),
    LootEntry.item(ItemType.ROYAL_SWORD),
    LootEntry.item(ItemType.MOLTEN_AXE),
    LootEntry.item(ItemType.WAND)
]

LOOT_ITEMS_4 = [
    LootEntry.item(ItemType.WINGED_HELMET),
    LootEntry.item(ItemType.ELVEN_ARMOR),
    LootEntry.item(ItemType.ELITE_ARMOR),
    LootEntry.item(ItemType.GLADIATOR_ARMOR),
    LootEntry.item(ItemType.FREEZING_GAUNTLET),
    LootEntry.item(ItemType.WIZARDS_COWL),
    LootEntry.item(ItemType.NOBLE_DEFENDER)
]

LOOT_POTIONS_1 = [
    LootEntry.consumable(ConsumableType.HEALTH_LESSER),
    LootEntry.consumable(ConsumableType.MANA_LESSER)
]

LOOT_POTIONS_2 = [
    LootEntry.consumable(ConsumableType.HEALTH),
    LootEntry.consumable(ConsumableType.MANA),
    LootEntry.consumable(ConsumableType.SPEED),
    LootEntry.consumable(ConsumableType.WARP_STONE)
]

LOOT_TABLE_1 = LootTable([
    LootGroup(1, [LootEntry.money(1), LootEntry.money(2)], 0.1),
    LootGroup(1, LOOT_POTIONS_1, 0.05),
    LootGroup(1, LOOT_ITEMS_1, 0.05),
])

LOOT_TABLE_2 = LootTable([
    LootGroup(1, [LootEntry.money(1), LootEntry.money(2), LootEntry.money(3)], 0.1),
    LootGroup(1, LOOT_POTIONS_1, 0.05),
    LootGroup(1, LOOT_ITEMS_1 + LOOT_ITEMS_2 + LOOT_ITEMS_3, 0.05),
    LootGroup.single(LootEntry.item(ItemType.GOLD_NUGGET), 0.01),
])

LOOT_TABLE_3 = LootTable([
    LootGroup(1, [LootEntry.money(2), LootEntry.money(3), LootEntry.money(4)], 0.2),
    LootGroup(1, LOOT_POTIONS_1 + LOOT_POTIONS_2, 0.1),
    LootGroup(1, LOOT_ITEMS_2 + LOOT_ITEMS_3 + LOOT_ITEMS_4, 0.1),
    LootGroup.single(LootEntry.item(ItemType.GOLD_NUGGET), 0.015),
    LootGroup.single(LootEntry.item(ItemType.SAPHIRE), 0.005)
])

LOOT_TABLE_4 = LootTable([
    LootGroup(1, [LootEntry.money(2), LootEntry.money(3), LootEntry.money(4)], 0.4),
    LootGroup(1, LOOT_POTIONS_1 + LOOT_POTIONS_2, 0.2),
    LootGroup(1, LOOT_ITEMS_3 + LOOT_ITEMS_4, 0.2),
    LootGroup.single(LootEntry.item(ItemType.GOLD_NUGGET), 0.1),
    LootGroup.single(LootEntry.item(ItemType.SAPHIRE), 0.02),
])
