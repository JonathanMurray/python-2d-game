from pythongame.core.common import ItemType, ConsumableType
from pythongame.core.loot import LootTable, LootGroup, LootEntry

LOOT_ITEMS_1 = [
    LootEntry.item(ItemType.MESSENGERS_HAT),
    LootEntry.item(ItemType.AMULET_OF_MANA_1),
    LootEntry.item(ItemType.BLESSED_SHIELD_1),
    LootEntry.item(ItemType.SOLDIERS_HELMET_1),
    LootEntry.item(ItemType.BLUE_ROBE_1),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_1),
    LootEntry.item(ItemType.WOODEN_SHIELD),
    LootEntry.item(ItemType.LEATHER_COWL),
]

LOOT_ITEMS_2 = [
    LootEntry.item(ItemType.SWORD_OF_LEECHING),
    LootEntry.item(ItemType.ROD_OF_LIGHTNING),
    LootEntry.item(ItemType.AMULET_OF_MANA_2),
    LootEntry.item(ItemType.BLESSED_SHIELD_2),
    LootEntry.item(ItemType.SOLDIERS_HELMET_2),
    LootEntry.item(ItemType.BLUE_ROBE_2),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_2),
    LootEntry.item(ItemType.WIZARDS_COWL),
    LootEntry.item(ItemType.ZULS_AEGIS),
    LootEntry.item(ItemType.GOATS_RING),
    LootEntry.item(ItemType.BLOOD_AMULET),
    LootEntry.item(ItemType.KNIGHTS_ARMOR),
    LootEntry.item(ItemType.ELVEN_ARMOR),
    LootEntry.item(ItemType.WINGED_HELMET),
    LootEntry.item(ItemType.ELITE_ARMOR),
    LootEntry.item(ItemType.RING_OF_POWER)
]

LOOT_POTIONS_1 = [
    LootEntry.consumable(ConsumableType.HEALTH_LESSER),
    LootEntry.consumable(ConsumableType.MANA_LESSER)
]

LOOT_POTIONS_2 = [
    LootEntry.consumable(ConsumableType.HEALTH),
    LootEntry.consumable(ConsumableType.MANA),
    LootEntry.consumable(ConsumableType.SPEED)
]

LOOT_TABLE_1 = LootTable([
    LootGroup.single(LootEntry.money(1), 0.1),
    LootGroup(1, LOOT_POTIONS_1, 0.05),
    LootGroup(1, LOOT_ITEMS_1, 0.02),
])

LOOT_TABLE_2 = LootTable([
    LootGroup(1, [LootEntry.money(1), LootEntry.money(2)], 0.6),
    LootGroup(1, LOOT_POTIONS_1, 0.15),
    LootGroup(1, LOOT_POTIONS_2, 0.05),
    LootGroup(1, LOOT_ITEMS_1, 0.05),
    LootGroup.single(LootEntry.item(ItemType.GOLD_NUGGET), 0.015),
    LootGroup.single(LootEntry.item(ItemType.SAPHIRE), 0.005)
])

LOOT_TABLE_3 = LootTable([
    LootGroup(1, [LootEntry.money(1), LootEntry.money(2)], 0.4),
    LootGroup(1, LOOT_POTIONS_1 + LOOT_POTIONS_2, 0.2),
    LootGroup(1, LOOT_ITEMS_1 + LOOT_ITEMS_2, 0.25),
    LootGroup.single(LootEntry.item(ItemType.GOLD_NUGGET), 0.1),
    LootGroup.single(LootEntry.item(ItemType.SAPHIRE), 0.02),
])
