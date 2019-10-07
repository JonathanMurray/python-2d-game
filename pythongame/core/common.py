import random
from enum import Enum
from typing import NewType

Millis = NewType('Millis', int)

PLAYER_ENTITY_SIZE = (30, 30)


class SceneId(Enum):
    PICKING_HERO = 1
    PLAYING = 2
    PAUSED = 3


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def get_all_directions():
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


class ConsumableType(Enum):
    HEALTH_LESSER = 1
    HEALTH = 2
    MANA_LESSER = 11
    MANA = 12
    SPEED = 21
    INVISIBILITY = 22
    BREW = 50
    WARP_STONE = 60
    SCROLL_SUMMON_DRAGON = 101


class NpcType(Enum):
    CHEST = 1
    NECROMANCER = 3
    WARRIOR = 4
    RAT_1 = 5
    RAT_2 = 6
    DARK_REAPER = 7
    GOBLIN_WARLOCK = 8
    MUMMY = 9
    GOBLIN_WORKER = 10
    GOBLIN_SPEARMAN = 11
    GOBLIN_SPEARMAN_ELITE = 12
    GOBLIN_WARRIOR = 13
    ZOMBIE = 14
    VETERAN = 15
    ICE_WITCH = 16
    WARRIOR_KING = 17
    NEUTRAL_DWARF = 100
    NEUTRAL_NOMAD = 101
    NEUTRAL_NINJA = 102
    NEUTRAL_SORCERER = 103
    NEUTRAL_YOUNG_SORCERESS = 104
    NEUTRAL_WARPSTONE_MERCHANT = 105
    PLAYER_SUMMON_DRAGON = 200


class WallType(Enum):
    WALL = 1
    STATUE = 2
    WALL_DIRECTIONAL_N = 11
    WALL_DIRECTIONAL_NE = 12
    WALL_DIRECTIONAL_E = 13
    WALL_DIRECTIONAL_SE = 14
    WALL_DIRECTIONAL_S = 15
    WALL_DIRECTIONAL_SW = 16
    WALL_DIRECTIONAL_W = 17
    WALL_DIRECTIONAL_NW = 18
    WALL_DIRECTIONAL_POINTY_NE = 19
    WALL_DIRECTIONAL_POINTY_SE = 20
    WALL_DIRECTIONAL_POINTY_SW = 21
    WALL_DIRECTIONAL_POINTY_NW = 22
    WALL_CHAIR = 30
    ALTAR = 31
    SHELF_EMPTY = 40
    SHELF_HELMETS = 41
    SHELF_ARMORS = 42
    BARREL_1 = 50
    BARREL_2 = 51
    BARREL_3 = 52
    BARREL_4 = 53
    BARREL_5 = 54
    BARREL_6 = 55


class AbilityType(Enum):
    HEAL = 1
    FIREBALL = 2
    CHANNEL_ATTACK = 4
    TELEPORT = 5
    FROST_NOVA = 6
    WHIRLWIND = 7
    ENTANGLING_ROOTS = 8
    SWORD_SLASH = 10
    BLOOD_LUST = 11
    CHARGE = 12
    STOMP = 13
    SHIV = 14
    SNEAK = 15
    INFUSE_DAGGER = 16
    DASH = 17
    KILL_EVERYTHING = 18


class Sprite(Enum):
    EFFECT_ABILITY_FROST_NOVA = 3
    PROJECTILE_PLAYER_FIREBALL = 11
    PROJECTILE_PLAYER_MAGIC_MISSILE = 12
    PROJECTILE_PLAYER_WHIRLWIND = 13
    PROJECTILE_ENEMY_GOBLIN_WARLOCK = 14
    PROJECTILE_PLAYER_ENTANGLING_ROOTS = 15
    POTION_HEALTH = 101
    POTION_HEALTH_LESSER = 102
    POTION_MANA = 103
    POTION_MANA_LESSER = 104
    CONSUMABLE_SCROLL_SUMMON_DRAGON = 105
    POTION_INVIS = 106
    POTION_SPEED = 107
    POTION_BREW = 108
    CONSUMABLE_WARPSTONE = 109
    ENEMY_NECROMANCER = 201
    ENEMY_RAT_1 = 202
    ENEMY_RAT_2 = 203
    ENEMY_DARK_REAPER = 204
    ENEMY_GOBLIN_WARLOCK = 205
    ENEMY_MUMMY = 206
    ENEMY_WARRIOR = 207
    ENEMY_CHEST = 208
    ENEMY_GOBLIN_WORKER = 209
    ENEMY_GOBLIN_SPEARMAN = 210
    ENEMY_GOBLIN_SPEARMAN_ELITE = 211
    ENEMY_GOBLIN_WARRIOR = 212
    ENEMY_ZOMBIE = 213
    ENEMY_VETERAN = 214
    ENEMY_ICE_WITCH = 215
    ENEMY_WARRIOR_KING = 216
    PLAYER_SUMMON_DRAGON = 250
    NEUTRAL_NPC_DWARF = 260
    NEUTRAL_NPC_NOMAD = 261
    NEUTRAL_NPC_NINJA = 262
    NEUTRAL_NPC_SORCERER = 263
    NEUTRAL_NPC_YOUNG_SORCERESS = 264
    NEUTRAL_WARPSTONE_MERCHANT = 265
    ITEM_AMULET_OF_MANA = 301
    ITEM_MESSENGERS_HAT = 302
    ITEM_ROD_OF_LIGHTNING = 303
    ITEM_SWORD_OF_LEECHING = 304
    ITEM_SOLDIERS_HELMET = 305
    ITEM_BLESSED_SHIELD = 306
    ITEM_STAFF_OF_FIRE = 307
    ITEM_BLUE_ROBE = 308
    ITEM_ORB_OF_THE_MAGI = 309
    ITEM_WIZARDS_COWL = 310
    ITEM_ZULS_AEGIS = 311
    ITEM_KNIGHTS_ARMOR = 312
    ITEM_GOATS_RING = 313
    ITEM_BLOOD_AMULET = 314
    ITEM_WOODEN_SHIELD = 315
    ITEM_ELVEN_ARMOR = 316
    ITEM_GOLD_NUGGET = 317
    ITEM_SAPHIRE = 318
    ITEM_LEATHER_COWL = 319
    ITEM_WINGED_HELMET = 320
    ITEM_ELITE_ARMOR = 321
    ITEM_RING_OF_POWER = 322
    ITEM_LEATHER_ARMOR = 323
    ITEM_FREEZING_GAUNTLET = 324
    ITEM_ROYAL_DAGGER = 325
    ITEM_ROYAL_SWORD = 326
    ITEM_MOLTEN_AXE = 327
    ITEM_ORB_OF_WISDOM = 328
    ITEM_ORB_OF_LIFE = 329
    ITEM_WAND = 330
    ITEM_GLADIATOR_ARMOR = 331
    ITEM_NOBLE_DEFENDER = 332
    ITEM_FROG = 333
    COINS_1 = 350
    COINS_2 = 351
    COINS_5 = 352
    DECORATION_GROUND_STONE = 401
    DECORATION_GROUND_STONE_GRAY = 402
    DECORATION_PLANT = 403
    DECORATION_ENTANGLING_ROOTS_EFFECT = 404
    WALL = 501
    WALL_STATUE = 502
    WALL_ALTAR = 503
    WALL_DIRECTIONAL_N = 511
    WALL_DIRECTIONAL_NE = 512
    WALL_DIRECTIONAL_E = 513
    WALL_DIRECTIONAL_SE = 514
    WALL_DIRECTIONAL_S = 515
    WALL_DIRECTIONAL_SW = 516
    WALL_DIRECTIONAL_W = 517
    WALL_DIRECTIONAL_NW = 518
    WALL_DIRECTIONAL_POINTY_NE = 519
    WALL_DIRECTIONAL_POINTY_SE = 520
    WALL_DIRECTIONAL_POINTY_SW = 521
    WALL_DIRECTIONAL_POINTY_NW = 522
    WALL_CHAIR = 530
    WALL_SHELF_EMPTY = 540
    WALL_SHELF_HELMETS = 541
    WALL_SHELF_ARMORS = 542
    WALL_BARREL_1 = 550
    WALL_BARREL_2 = 551
    WALL_BARREL_3 = 552
    WALL_BARREL_4 = 553
    WALL_BARREL_5 = 554
    WALL_BARREL_6 = 555
    PORTAL_DISABLED = 600
    PORTAL_BLUE = 601
    PORTAL_GREEN = 602
    PORTAL_RED = 603
    PORTAL_DARK = 604
    WARP_POINT = 650
    HERO_MAGE = 700
    HERO_WARRIOR = 701
    HERO_ROGUE = 702
    HERO_GOD = 703


class BuffType(Enum):
    HEALING_OVER_TIME = 1
    INCREASED_MOVE_SPEED = 3
    INVISIBILITY = 4
    CHANNELING_MAGIC_MISSILES = 5
    REDUCED_MOVEMENT_SPEED = 6
    INVULNERABILITY = 7
    STUNNED_BY_WHIRLWIND = 8
    ENEMY_GOBLIN_WARLOCK_BURNT = 9
    ROOTED_BY_ENTANGLING_ROOTS = 10
    SUMMON_DIE_AFTER_DURATION = 11
    BLOOD_LUST = 13
    CHARGING = 14
    STUNNED_FROM_CHARGE_IMPACT = 15
    RECOVERING_AFTER_ABILITY = 17
    CHANNELING_STOMP = 18
    STUNNED_BY_STOMP = 19
    SNEAKING = 20
    AFTER_SNEAKING = 21
    STUNNED_BY_AEGIS_ITEM = 22
    DEBUFFED_BY_GOATS_RING = 23
    DAMAGED_BY_INFUSED_DAGGER = 26
    AFTER_DASH = 27
    RESTORING_HEALTH_FROM_BREW = 28
    DEBUFFED_BY_FREEZING_GAUNTLET = 29
    SLOWED_BY_ICE_WITCH = 30
    SLOWED_FROM_NOBLE_DEFENDER = 31
    TELEPORTING_WITH_PORTAL = 32
    TELEPORTING_WITH_WARP_STONE = 33
    TELEPORTING_WITH_WARP_POINT = 34
    BEING_SPAWNED = 35


class ItemType(Enum):
    MESSENGERS_HAT = 1
    SWORD_OF_LEECHING = 3
    ROD_OF_LIGHTNING = 4
    STAFF_OF_FIRE = 7
    AMULET_OF_MANA_1 = 10
    AMULET_OF_MANA_2 = 11
    AMULET_OF_MANA_3 = 12
    BLESSED_SHIELD_1 = 20
    BLESSED_SHIELD_2 = 21
    BLESSED_SHIELD_3 = 22
    SOLDIERS_HELMET_1 = 30
    SOLDIERS_HELMET_2 = 31
    SOLDIERS_HELMET_3 = 32
    BLUE_ROBE_1 = 40
    BLUE_ROBE_2 = 41
    BLUE_ROBE_3 = 42
    ORB_OF_THE_MAGI_1 = 50
    ORB_OF_THE_MAGI_2 = 51
    ORB_OF_THE_MAGI_3 = 52
    ORB_OF_WISDOM_1 = 53
    ORB_OF_WISDOM_2 = 54
    ORB_OF_WISDOM_3 = 55
    ORB_OF_LIFE_1 = 56
    ORB_OF_LIFE_2 = 57
    ORB_OF_LIFE_3 = 58
    WIZARDS_COWL = 60
    ZULS_AEGIS = 70
    KNIGHTS_ARMOR = 71
    GOATS_RING = 72
    BLOOD_AMULET = 73
    WOODEN_SHIELD = 74
    ELVEN_ARMOR = 75
    GOLD_NUGGET = 76
    SAPHIRE = 77
    LEATHER_COWL = 78
    WINGED_HELMET = 79
    ELITE_ARMOR = 80
    RING_OF_POWER = 81
    LEATHER_ARMOR = 82
    FREEZING_GAUNTLET = 83
    ROYAL_DAGGER = 84
    ROYAL_SWORD = 85
    MOLTEN_AXE = 86
    WAND = 87
    GLADIATOR_ARMOR = 88
    NOBLE_DEFENDER = 89
    FROG = 90


class ProjectileType(Enum):
    PLAYER_FIREBALL = 1
    PLAYER_MAGIC_MISSILE = 2
    PLAYER_WHIRLWIND = 3
    PLAYER_ENTANGLING_ROOTS = 4
    ENEMY_GOBLIN_WARLOCK = 101


class SoundId(Enum):
    ABILITY_FIREBALL = 1
    ABILITY_WHIRLWIND = 2
    ABILITY_TELEPORT = 3
    ABILITY_ENTANGLING_ROOTS = 4
    ABILITY_CHARGE = 5
    ABILITY_SHIV = 6
    ABILITY_SNEAK = 7
    ABILITY_INFUSE_DAGGER = 8
    ABILITY_DASH = 9
    ABILITY_SLASH = 10
    ABILITY_STOMP = 11
    ABILITY_BLOODLUST = 12
    POTION = 50
    EVENT_PLAYER_LEVELED_UP = 100
    EVENT_PICKED_UP = 101
    EVENT_PLAYER_DIED = 102
    EVENT_ENEMY_DIED = 103
    EVENT_PICKED_UP_MONEY = 104
    EVENT_PURCHASED_SOMETHING = 105
    WARNING = 200
    INVALID_ACTION = 201
    PLAYER_PAIN = 300
    ENEMY_ATTACK_GOBLIN_WARLOCK = 400
    ENEMY_ATTACK = 401
    ENEMY_ATTACK_WAS_BLOCKED = 402
    DEATH_RAT = 500
    DEATH_ZOMBIE = 501
    UI_ITEM_WAS_MOVED = 600
    UI_START_DRAGGING_ITEM = 601
    DIALOG = 700


class PortalId(Enum):
    A_BASE = 1
    A_REMOTE = 2
    B_BASE = 3
    B_REMOTE = 4
    C_BASE = 5
    C_REMOTE = 6
    D_BASE = 7
    D_REMOTE = 8


class HeroId(Enum):
    MAGE = 1
    WARRIOR = 2
    ROGUE = 3
    GOD = 4


class UiIconSprite(Enum):
    POTION_HEALTH_LESSER = 1
    POTION_HEALTH = 2
    POTION_MANA_LESSER = 3
    POTION_MANA = 4
    POTION_SPEED = 11
    POTION_INVISIBILITY = 12
    CONSUMABLE_SCROLL_SUMMON_DRAGON = 13
    POTION_BREW = 14
    CONSUMABLE_WARPSTONE = 15
    ABILITY_FIREBALL = 101
    ABILITY_HEAL = 102
    ABILITY_MAGIC_MISSILE = 103
    ABILITY_TELEPORT = 104
    ABILITY_FROST_NOVA = 105
    ABILITY_WHIRLWIND = 106
    ABILITY_ENTANGLING_ROOTS = 107
    ABILITY_SWORD_SLASH = 109
    ABILITY_BLOODLUST = 110
    ABILITY_CHARGE = 111
    ABILITY_STOMP = 112
    ABILITY_SHIV = 113
    ABILITY_SNEAK = 114
    ABILITY_INFUSE_DAGGER = 115
    ABILITY_DASH = 116
    ABILITY_KILL_EVERYTHING = 117
    ITEM_MESSENGERS_HAT = 201
    ITEM_AMULET_OF_MANA = 202
    ITEM_SWORD_OF_LEECHING = 203
    ITEM_ROD_OF_LIGHTNING = 204
    ITEM_SOLDIERS_HELMET = 205
    ITEM_BLESSED_SHIELD = 206
    ITEM_STAFF_OF_FIRE = 207
    ITEM_BLUE_ROBE = 208
    ITEM_ORB_OF_THE_MAGI = 209
    ITEM_WIZARDS_COWL = 210
    ITEM_ZULS_AEGIS = 211
    ITEM_KNIGHTS_ARMOR = 212
    ITEM_GOATS_RING = 213
    ITEM_BLOOD_AMULET = 214
    ITEM_WOODEN_SHIELD = 215
    ITEM_ELVEN_ARMOR = 216
    ITEM_GOLD_NUGGET = 217
    ITEM_SAPHIRE = 218
    ITEM_LEATHER_COWL = 219
    ITEM_WINGED_HELMET = 220
    ITEM_ELITE_ARMOR = 221
    ITEM_RING_OF_POWER = 222
    ITEM_LEATHER_ARMOR = 223
    ITEM_FREEZING_GAUNTLET = 224
    ITEM_ROYAL_DAGGER = 225
    ITEM_ROYAL_SWORD = 226
    ITEM_MOLTEN_AXE = 227
    ITEM_ORB_OF_WISDOM = 228
    ITEM_ORB_OF_LIFE = 229
    ITEM_WAND = 230
    ITEM_GLADIATOR_ARMOR = 231
    ITEM_NOBLE_DEFENDER = 232
    ITEM_FROG = 233
    MAP_EDITOR_TRASHCAN = 301
    MAP_EDITOR_RECYCLING = 302
    INVENTORY_TEMPLATE_HELMET = 400
    INVENTORY_TEMPLATE_CHEST = 401
    INVENTORY_TEMPLATE_MAINHAND = 402
    INVENTORY_TEMPLATE_OFFHAND = 403
    INVENTORY_TEMPLATE_NECK = 404
    INVENTORY_TEMPLATE_RING = 405


# Portraits that are shown in UI (player portrait and dialog portraits)
class PortraitIconSprite(Enum):
    VIKING = 2
    NOMAD = 3
    NINJA = 4
    SORCERER = 5
    YOUNG_SORCERESS = 6
    WARPSTONE_MERCHANT = 7
    HERO_MAGE = 10
    HERO_WARRIOR = 11
    HERO_ROGUE = 12
    HERO_GOD = 13


# Use to handle timing-related boilerplate for buffs, items, enemy behaviours, etc
class PeriodicTimer:
    def __init__(self, cooldown: Millis):
        self.cooldown = cooldown
        self.time_until_next_run = cooldown

    # notify the timer of how much time has passed since the last call
    # the timer checks if enough time has passed. If it has, it resets
    # and returns True.
    def update_and_check_if_ready(self, time_passed: Millis) -> bool:
        self.time_until_next_run -= time_passed
        if self.time_until_next_run <= 0:
            self.time_until_next_run += self.cooldown
            return True
        return False


def get_random_hint():
    hints = [
        "Hold Shift to see more info about lootable items",
        "Press Space to interact with NPCs and objects",
        "Reaching certain levels unlocks new abilities",
        "Use the number keys for potions and other consumables",
        "Gold coins are looted by simply walking over them",
        "If you die, you'll respawn but lose exp points",
        "Use magic statues and warpstones to teleport long distances",
        "Hover over things with the mouse cursor to get more info",
        "Drag inventory items and consumables with the mouse cursor",
        "Equip items by dragging them to the appropriate inventory slot"
    ]
    return random.choice(hints)
