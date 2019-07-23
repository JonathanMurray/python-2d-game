from pythongame.core.common import ItemType, ConsumableType
from pythongame.core.loot import LootTable, LootGroup, LootEntry

LOOT_ITEMS_1 = [
    LootEntry.item(ItemType.WINGED_BOOTS),
    LootEntry.item(ItemType.AMULET_OF_MANA_1),
    LootEntry.item(ItemType.BLESSED_SHIELD_1),
    LootEntry.item(ItemType.SOLDIERS_HELMET_1),
    LootEntry.item(ItemType.BLUE_ROBE_1),
    LootEntry.item(ItemType.ORB_OF_THE_MAGI_1),
    LootEntry.item(ItemType.KNIGHTS_ARMOR)
]

POTIONS_1 = [
    LootEntry.consumable(ConsumableType.HEALTH_LESSER),
    LootEntry.consumable(ConsumableType.MANA_LESSER)
]

LOOT_TABLE_1 = LootTable([LootGroup.single(LootEntry.money(1), 0.1), LootGroup(1, POTIONS_1, 0.05)])

LOOT_TABLE_2 = LootTable([
    LootGroup(1, [LootEntry.money(1), LootEntry.money(2)], 0.6),
    LootGroup(1, POTIONS_1, 0.2),
    LootGroup(1, LOOT_ITEMS_1, 0.05)
])
