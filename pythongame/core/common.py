import random
from enum import Enum
from typing import NewType, Optional, Any, List, Callable, Union, Tuple

Millis = NewType('Millis', int)

PLAYER_ENTITY_SIZE = (30, 30)


class Observable:
    def __init__(self):
        self._observers: List[Callable[[Any], Any]] = []

    def register_observer(self, observer: Callable[[Any], Any]):
        self._observers.append(observer)

    def notify(self, event):
        for observer in self._observers:
            # print("DEBUG Notifying observer " + str(observer) + ": " + str(event))
            observer(event)


class SceneId(Enum):
    STARTING_PROGRAM = 1
    PICKING_HERO = 2
    CREATING_GAME_WORLD = 3
    PLAYING = 4
    PAUSED = 5
    VICTORY_SCREEN = 6
    CHALLENGE_COMPLETE_SCREEN = 7


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


def get_all_directions():
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


class HeroUpgradeId(Enum):
    ARMOR = 1
    DAMAGE = 2
    MAX_HEALTH = 3
    MAX_MANA = 4
    HEALTH_REGEN = 5
    MANA_REGEN = 6
    MOVE_SPEED = 7
    MAGIC_RESIST = 8
    ABILITY_WHIRLWIND_STUN = 10
    ABILITY_FIREBALL_BURN = 11
    ABILITY_ENTANGLING_ROOTS_COOLDOWN = 12
    ABILITY_FIREBALL_MANA_COST = 13
    ABILITY_ARCANE_FIRE_COOLDOWN = 14
    ABILITY_STEALTH_MANA_COST = 20
    ABILITY_SHIV_SNEAK_BONUS_DAMAGE = 21
    ABILITY_DASH_KILL_RESET = 22
    ABILITY_SHIV_FULL_HEALTH_BONUS_DAMAGE = 23
    ABILITY_STEALTH_MOVEMENT_SPEED = 24
    ABILITY_DASH_MOVEMENT_SPEED = 25
    ABILITY_CHARGE_MELEE = 30
    ABILITY_SLASH_AOE_BONUS_DAMAGE = 31
    ABILITY_BLOODLUST_DURATION = 32
    ABILITY_SLASH_CD = 33
    ABILITY_CHARGE_RESET_STOMP_COOLDOWN = 34
    MAGE_LIGHT_FOOTED = 50
    WARRIOR_RETRIBUTION = 51


class ConsumableType(Enum):
    HEALTH_LESSER = 1
    HEALTH = 2
    MANA_LESSER = 11
    MANA = 12
    SPEED = 21
    INVISIBILITY = 22
    POWER = 23
    MAGIC_RESIST = 24
    BREW = 50
    WARP_STONE = 60
    ACID_BOMB = 70
    SCROLL_SUMMON_DRAGON = 101


class NpcType(Enum):
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
    SKELETON_MAGE = 18
    ZOMBIE_FAST = 19
    SKELETON_BOSS = 20
    HUMAN_SUMMONER = 21
    FIRE_DEMON = 22
    NEUTRAL_DWARF = 100
    NEUTRAL_NOMAD = 101
    NEUTRAL_NINJA = 102
    NEUTRAL_SORCERER = 103
    NEUTRAL_YOUNG_SORCERESS = 104
    NEUTRAL_WARPSTONE_MERCHANT = 105
    NEUTRAL_CHALLENGE_STARTER = 107
    NEUTRAL_FROG = 108
    NEUTRAL_TALENT_MASTER = 109
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
    BASKET_EMPTY = 60
    BASKET_FRUIT = 61
    STONE_CROSS_FLOWERS = 70
    CHAIR_RIGHT = 80
    CHAIR_DOWN = 81
    CHAIR_LEFT = 82
    CHAIR_UP = 83
    SIGN_SMALL = 90
    SIGN_MULTI = 91
    SIGN_LARGE_EMPTY = 92
    SIGN_LARGE_NOTES = 93
    WEAPON_RACK = 100
    PILLAR = 110
    LIGHT_POLE = 120
    WELL = 130
    BENCH_MIRROR = 140
    BED_1 = 150
    BED_2 = 151
    BED_3 = 152
    PILLOW = 160
    PILLOWS_2 = 161
    DECORATED_TABLE = 170


class AbilityType(Enum):
    HEAL = 1
    FIREBALL = 2
    ARCANE_FIRE = 4
    TELEPORT = 5
    FROST_NOVA = 6
    WHIRLWIND = 7
    ENTANGLING_ROOTS = 8
    SWORD_SLASH = 10
    BLOOD_LUST = 11
    CHARGE = 12
    STOMP = 13
    SHIV = 14
    STEALTH = 15
    INFUSE_DAGGER = 16
    DASH = 17
    KILL_EVERYTHING = 18
    ITEM_ZULS_AEGIS = 100
    ITEM_LICH_ARMOR = 101
    ITEM_ROD_OF_LIGHTNING = 102
    ITEM_WINGED_HELMET = 103
    ITEM_CANDLE = 104
    ITEM_WHIP = 105


class Sprite(Enum):
    NONE = 0
    EFFECT_ABILITY_FROST_NOVA = 3
    PROJECTILE_PLAYER_FIREBALL = 11
    PROJECTILE_PLAYER_ARCANE_FIRE = 12
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
    ELIXIR_POWER = 110
    ELIXIR_MAGIC_RESIST = 111
    CONSUMABLE_ACID_BOMB = 112
    ENEMY_NECROMANCER = 201
    ENEMY_RAT_1 = 202
    ENEMY_RAT_2 = 203
    ENEMY_DARK_REAPER = 204
    ENEMY_GOBLIN_WARLOCK = 205
    ENEMY_MUMMY = 206
    ENEMY_WARRIOR = 207
    ENEMY_GOBLIN_WORKER = 209
    ENEMY_GOBLIN_SPEARMAN = 210
    ENEMY_GOBLIN_SPEARMAN_ELITE = 211
    ENEMY_GOBLIN_WARRIOR = 212
    ENEMY_ZOMBIE = 213
    ENEMY_VETERAN = 214
    ENEMY_ICE_WITCH = 215
    ENEMY_WARRIOR_KING = 216
    ENEMY_SKELETON_MAGE = 217
    ENEMY_ZOMBIE_FAST = 218
    ENEMY_SKELETON_BOSS = 219
    ENEMY_HUMAN_SUMMONER = 220
    ENEMY_FIRE_DEMON = 221
    PLAYER_SUMMON_DRAGON = 250
    NEUTRAL_NPC_DWARF = 260
    NEUTRAL_NPC_NOMAD = 261
    NEUTRAL_NPC_NINJA = 262
    NEUTRAL_NPC_SORCERER = 263
    NEUTRAL_NPC_YOUNG_SORCERESS = 264
    NEUTRAL_WARPSTONE_MERCHANT = 265
    NEUTRAL_NPC_CHALLENGE_STARTER = 267
    NEUTRAL_NPC_FROG = 268
    NEUTRAL_NPC_TALENT_MASTER = 269
    ITEM_AMULET_OF_MANA = 301
    ITEM_MESSENGERS_HAT = 302
    ITEM_ROD_OF_LIGHTNING = 303
    ITEM_SKULL_STAFF = 304
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
    ITEM_SAPPHIRE = 318
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
    ITEM_HATCHET = 334
    ITEM_ELITE_HELMET = 335
    ITEM_STONE_AMULET = 336
    ITEM_TORN_DOCUMENT = 337
    ITEM_KEY = 338
    ITEM_WOODEN_SWORD = 339
    ITEM_DRUIDS_RING = 340
    ITEM_WARLOCKS_COWL = 341
    ITEM_LICH_ARMOR = 342
    ITEM_WARLORDS_ARMOR = 343
    ITEM_HEALING_WAND = 344
    ITEM_SKULL_SHIELD = 345
    ITEM_THIEFS_MASK = 346
    ITEM_SERPENT_SWORD = 347
    ITEM_WHIP = 348
    ITEM_CLEAVER = 349
    ITEM_DESERT_BLADE = 350
    ITEM_PRACTICE_SWORD = 351
    ITEM_NOVICE_WAND = 352
    ITEM_SORCERESS_ROBE = 353
    ITEM_BLESSED_CHALICE = 354
    ITEM_NECKLACE_OF_SUFFERING = 355
    ITEM_FIRE_WAND = 356
    ITEM_FEATHER_HAT = 357
    ITEM_CANDLE = 358
    ITEM_BRONZE_RING = 359
    ITEM_FIRE_GAUNTLET = 360
    ITEM_SKULL_SWORD = 361
    ITEM_SUN_SHIELD = 362
    ITEM_CORRUPTED_ORB = 363
    ITEM_PORTAL_KEY = 364
    COINS_1 = 400
    COINS_2 = 401
    COINS_5 = 402
    DECORATION_GROUND_STONE = 450
    DECORATION_GROUND_STONE_GRAY = 451
    DECORATION_PLANT = 452
    DECORATION_ENTANGLING_ROOTS_EFFECT = 453
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
    WALL_CHAIR_RIGHT = 530
    WALL_CHAIR_DOWN = 531
    WALL_CHAIR_LEFT = 532
    WALL_CHAIR_UP = 533
    WALL_SHELF_EMPTY = 540
    WALL_SHELF_HELMETS = 541
    WALL_SHELF_ARMORS = 542
    WALL_BARREL_1 = 550
    WALL_BARREL_2 = 551
    WALL_BARREL_3 = 552
    WALL_BARREL_4 = 553
    WALL_BARREL_5 = 554
    WALL_BARREL_6 = 555
    WALL_BASKET_EMPTY = 560
    WALL_BASKET_FRUIT = 561
    WALL_STONE_CROSS_FLOWERS = 570
    WALL_SIGN_SMALL = 580
    WALL_SIGN_MULTI = 581
    WALL_SIGN_LARGE_EMPTY = 582
    WALL_SIGN_LARGE_NOTES = 583
    WALL_WEAPON_RACK = 590
    WALL_PILLAR = 600
    WALL_LIGHT_POLE = 610
    WALL_WELL = 620
    WALL_BENCH_MIRROR = 630
    WALL_BED_1 = 640
    WALL_BED_2 = 641
    WALL_BED_3 = 642
    WALL_PILLOW = 650
    WALL_PILLOWS_2 = 651
    WALL_DECORATED_TABLE = 660
    PORTAL_DISABLED = 1600
    PORTAL_BLUE = 1601
    PORTAL_GREEN = 1602
    PORTAL_RED = 1603
    PORTAL_DARK = 1604
    PORTAL_PURPLE = 1605
    WARP_POINT = 1650
    HERO_MAGE = 1700
    HERO_WARRIOR = 1701
    HERO_ROGUE = 1702
    HERO_GOD = 1703
    CHEST = 1800
    SHRINE = 1810
    DUNGEON_ENTRANCE = 1820
    MAP_EDITOR_SMART_FLOOR_1 = 1900
    MAP_EDITOR_SMART_FLOOR_2 = 1901
    MAP_EDITOR_SMART_FLOOR_3 = 1902
    MAP_EDITOR_SMART_FLOOR_4 = 1903


class BuffType(Enum):
    HEALING_OVER_TIME = 1
    INCREASED_MOVE_SPEED = 3
    INVISIBILITY = 4
    CHANNELING_ARCANE_FIRE = 5
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
    STEALTHING = 20
    STUNNED_BY_AEGIS_ITEM = 22
    DEBUFFED_BY_GOATS_RING = 23
    DAMAGED_BY_INFUSED_DAGGER = 26
    AFTER_DASH = 27
    RESTORING_HEALTH_FROM_BREW = 28
    DEBUFFED_BY_FREEZING_GAUNTLET = 29
    SLOWED_BY_ICE_WITCH = 30
    TELEPORTING_WITH_PORTAL = 32
    TELEPORTING_WITH_WARP_STONE = 33
    TELEPORTING_WITH_WARP_POINT = 34
    BEING_SPAWNED = 35
    BURNT_BY_FIREBALL = 36
    PROTECTED_BY_STONE_AMULET = 37
    ELIXIR_OF_POWER = 38
    BUFFED_BY_HEALING_WAND = 39
    ENEMY_GOBLIN_SPEARMAN_SPRINT = 40
    BLEEDING_FROM_CLEAVER_WEAPON = 41
    SPEED_BUFF_FROM_DASH = 42
    BUFFED_FROM_RETRIBUTION_TALENT = 43
    INCREASED_DAMAGE_FROM_NECKLACE_OF_SUFFERING = 44
    ELIXIR_OF_MAGIC_RESIST = 45
    ENEMY_SKELETON_BOSS_STUNNED_FROM_FIRING = 46
    POISONED_BY_ACID_BOMB = 47
    SHRINE_DAMAGE = 100
    SHRINE_ARMOR = 101
    SHRINE_MAGIC_RESIST = 102
    SHRINE_MOVE_SPEED = 103
    ITEM_WINGED_HELMET = 200
    ITEM_CANDLE = 201
    ITEM_WHIP = 202
    ITEM_BLOOD_AMULET = 203


class ItemType(Enum):
    MESSENGERS_HAT = 1
    SKULL_STAFF = 3
    ROD_OF_LIGHTNING = 4
    STAFF_OF_FIRE = 7
    AMULET_OF_MANA = 10
    BLESSED_SHIELD = 20
    SOLDIERS_HELMET = 30
    BLUE_ROBE = 40
    ORB_OF_THE_MAGI = 50
    ORB_OF_WISDOM = 53
    ORB_OF_LIFE = 56
    WIZARDS_COWL = 60
    ZULS_AEGIS = 70
    KNIGHTS_ARMOR = 71
    GOATS_RING = 72
    BLOOD_AMULET = 73
    WOODEN_SHIELD = 74
    ELVEN_ARMOR = 75
    GOLD_NUGGET = 76
    SAPPHIRE = 77
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
    QUEST_FROG = 90
    HATCHET = 91
    ELITE_HELMET = 92
    STONE_AMULET = 93
    TORN_DOCUMENT = 94
    QUEST_KEY = 95
    WOODEN_SWORD = 96
    DRUIDS_RING = 97
    WARLOCKS_COWL = 98
    LICH_ARMOR = 99
    WARLORDS_ARMOR = 100
    HEALING_WAND = 101
    SKULL_SHIELD = 102
    THIEFS_MASK = 103
    SERPENT_SWORD = 104
    WHIP = 105
    CLEAVER = 106
    DESERT_BLADE = 107
    PRACTICE_SWORD = 108
    NOVICE_WAND = 109
    SORCERESS_ROBE = 110
    BLESSED_CHALICE = 111
    NECKLACE_OF_SUFFERING = 112
    FIRE_WAND = 113
    FEATHER_HAT = 114
    CANDLE = 115
    BRONZE_RING = 116
    FIRE_GAUNTLET = 117
    SKULL_SWORD = 118
    SUN_SHIELD = 119
    QUEST_CORRUPTED_ORB = 120
    PORTAL_KEY = 121


class HeroStat(Enum):
    MAX_HEALTH = 1
    HEALTH_REGEN = 2
    MAX_MANA = 3
    MANA_REGEN = 4
    ARMOR = 5
    MOVEMENT_SPEED = 6
    LIFE_STEAL = 7
    BLOCK_AMOUNT = 8
    DODGE_CHANCE = 9
    DAMAGE = 10
    PHYSICAL_DAMAGE = 11
    MAGIC_DAMAGE = 12
    BLOCK_CHANCE = 13
    MAGIC_RESIST_CHANCE = 14
    MOVEMENT_IMPAIRING_RESIST_CHANCE = 15
    INCREASED_LOOT_MONEY_CHANCE = 16
    MANA_ON_KILL = 17
    LIFE_ON_KILL = 18
    INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE = 19


def _get_description(hero_stat: HeroStat, arg: str):
    if hero_stat == HeroStat.MAX_HEALTH:
        return "+" + arg + " max health"
    elif hero_stat == HeroStat.HEALTH_REGEN:
        return "+" + arg + " health regen"
    elif hero_stat == HeroStat.MAX_MANA:
        return "+" + arg + " max mana"
    elif hero_stat == HeroStat.MANA_REGEN:
        return "+" + arg + " mana regen"
    elif hero_stat == HeroStat.ARMOR:
        return arg + " armor"
    elif hero_stat == HeroStat.DAMAGE:
        return "+" + arg + " attack power"
    elif hero_stat == HeroStat.PHYSICAL_DAMAGE:
        return "+" + arg + " physical attack power"
    elif hero_stat == HeroStat.MAGIC_DAMAGE:
        return "+" + arg + " magic attack power"
    elif hero_stat == HeroStat.LIFE_STEAL:
        return "+" + arg + "% life steal"
    elif hero_stat == HeroStat.BLOCK_AMOUNT:
        return arg + " block"
    elif hero_stat == HeroStat.DODGE_CHANCE:
        return "+" + arg + "% dodge chance"
    elif hero_stat == HeroStat.MAGIC_RESIST_CHANCE:
        return "+" + arg + "% magic resist"
    elif hero_stat == HeroStat.BLOCK_CHANCE:
        return "+" + arg + "% block chance"
    elif hero_stat == HeroStat.INCREASED_LOOT_MONEY_CHANCE:
        return "+" + arg + "% money from enemies"
    elif hero_stat == HeroStat.MANA_ON_KILL:
        return "On kill: restore " + arg + " mana"
    elif hero_stat == HeroStat.LIFE_ON_KILL:
        return "On kill: gain " + arg + " health"
    elif hero_stat == HeroStat.INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE:
        return "+" + arg + "% increased chance to find rare items"
    else:
        raise Exception("Unhandled stat: " + str(hero_stat))


class StatModifier:
    def __init__(self, hero_stat: HeroStat, delta: Union[int, float]):
        self.hero_stat = hero_stat
        self.delta = delta

    def get_description(self):
        hero_stat = self.hero_stat
        delta = self.delta
        if hero_stat in [HeroStat.MAX_HEALTH, HeroStat.MAX_MANA, HeroStat.ARMOR, HeroStat.BLOCK_AMOUNT,
                         HeroStat.MANA_ON_KILL, HeroStat.LIFE_ON_KILL]:
            return _get_description(hero_stat, str(delta))
        elif hero_stat in [HeroStat.HEALTH_REGEN, HeroStat.MANA_REGEN]:
            return _get_description(hero_stat, "{:.1f}".format(delta))
        elif hero_stat in [HeroStat.DAMAGE, HeroStat.PHYSICAL_DAMAGE, HeroStat.MAGIC_DAMAGE, HeroStat.LIFE_STEAL,
                           HeroStat.DODGE_CHANCE, HeroStat.MAGIC_RESIST_CHANCE, HeroStat.BLOCK_CHANCE,
                           HeroStat.INCREASED_LOOT_MONEY_CHANCE, HeroStat.INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE]:
            return _get_description(hero_stat, str(int(round(delta * 100))))
        elif hero_stat == HeroStat.MOVEMENT_SPEED:
            if delta >= 0:
                return "Increases movement speed by " + str(int(delta * 100)) + "%"
            else:
                return "Reduces movement speed by " + str(int(delta * 100)) + "%"
        elif hero_stat == HeroStat.MOVEMENT_IMPAIRING_RESIST_CHANCE:
            if delta == 1:
                return "Immune to slows and stuns"
            else:
                return "+" + str(int(delta * 100)) + "% chance to resist slows and stuns"
        else:
            raise Exception("Unhandled stat: " + str(hero_stat))

    def __repr__(self):
        return "%s:%s" % (self.hero_stat, self.delta)


class StatModifierInterval:
    def __init__(self, hero_stat: HeroStat, interval: List[Union[int, float]]):
        self.hero_stat = hero_stat
        self.interval = interval

    def get_interval_description(self):
        hero_stat = self.hero_stat
        interval = self.interval

        if hero_stat in [HeroStat.MAX_HEALTH, HeroStat.MAX_MANA, HeroStat.ARMOR, HeroStat.BLOCK_AMOUNT,
                         HeroStat.MANA_ON_KILL, HeroStat.LIFE_ON_KILL]:
            if interval[0] == interval[-1]:
                return _get_description(hero_stat, str(interval[0]))
            else:
                return _get_description(hero_stat, "(" + str(interval[0]) + "-" + str(interval[-1]) + ")")
        elif hero_stat in [HeroStat.HEALTH_REGEN, HeroStat.MANA_REGEN]:
            if interval[0] == interval[-1]:
                return _get_description(hero_stat, "{:.1f}".format(interval[0]))
            else:
                return _get_description(hero_stat,
                                        "(" + "{:.1f}".format(interval[0]) + "-" + "{:.1f}".format(interval[-1]) + ")")
        elif hero_stat in [HeroStat.DAMAGE, HeroStat.PHYSICAL_DAMAGE, HeroStat.MAGIC_DAMAGE, HeroStat.LIFE_STEAL,
                           HeroStat.DODGE_CHANCE, HeroStat.MAGIC_RESIST_CHANCE, HeroStat.BLOCK_CHANCE,
                           HeroStat.INCREASED_LOOT_MONEY_CHANCE, HeroStat.INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE]:
            if interval[0] == interval[-1]:
                return _get_description(hero_stat, str(int(round(interval[0] * 100))))
            else:
                return _get_description(hero_stat,
                                        "(" + str(int(round(interval[0] * 100))) + "-" +
                                        str(int(round(interval[-1] * 100))) + ")")
        elif hero_stat == HeroStat.MOVEMENT_SPEED:
            if interval[0] == interval[-1]:
                return "Changes movement speed by " + str(int(interval[0] * 100)) + "%"
            else:
                return "Changes movement speed by (" + str(int(interval[0] * 100)) + "-" + \
                       str(int(interval[-1] * 100)) + ")%"
        elif hero_stat == HeroStat.MOVEMENT_IMPAIRING_RESIST_CHANCE:
            if interval[0] == interval[-1]:
                return "Changes slow/stun resistance chance by " + str(int(interval[0] * 100)) + "%"
            else:
                return "Changes slow/stun resistance chance by (" + str(int(interval[0] * 100)) + "-" + \
                       str(int(interval[-1] * 100)) + ")%"
        else:
            raise Exception("Unhandled stat: " + str(hero_stat))


class ItemSuffixData:
    def __init__(self, name_prefix: Optional[str], name_suffix: Optional[str], level_interval: Tuple[int, int],
                 stats: List[StatModifierInterval]):
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix
        self.level_interval = level_interval
        self.stats = stats


class ItemAffixId(Enum):
    MAX_HEALTH_1 = 0
    MAX_HEALTH_2 = 1
    MAX_MANA_1 = 10
    MAX_MANA_2 = 11
    HEALTH_REGEN_1 = 20
    HEALTH_REGEN_2 = 21
    MANA_REGEN_1 = 30
    MANA_REGEN_2 = 31
    MOVEMENT_SPEED = 40
    LIFE_STEAL = 50
    DAMAGE_1 = 60
    DAMAGE_2 = 61
    PHYSICAL_DAMAGE_1 = 70
    PHYSICAL_DAMAGE_2 = 71
    MAGIC_DAMAGE_1 = 80
    MAGIC_DAMAGE_2 = 81
    MAGIC_RESIST = 90
    DODGE_CHANCE = 100
    BLOCK_CHANCE = 110
    MOVEMENT_IMPAIR_IMMUNE = 120
    INCREASED_LOOT_MONEY = 130
    MANA_ON_KILL = 140
    LIFE_ON_KILL_1 = 150
    LIFE_ON_KILL_2 = 151
    INCREASED_LOOT_RARE_OR_UNIQUE_CHANCE = 160


class ItemId:
    def __init__(self, item_type: ItemType, name: str, base_stats: List[StatModifier], affix_stats: List[StatModifier]):
        self.item_type = item_type
        self.name = name
        self.base_stats = base_stats
        self.stats_string = self.build_stats_string(item_type, base_stats, affix_stats)
        self.affix_stats = affix_stats

    @staticmethod
    def build_stats_string(item_type: ItemType, base_stats: List[StatModifier], suffix_stats: List[StatModifier]):
        string = item_type.name + "~"
        for modifier in base_stats:
            string += ":%s:%s" % (modifier.hero_stat.name, modifier.delta)
        string += "~"
        if suffix_stats:
            for modifier in suffix_stats:
                string += ":%s:%s" % (modifier.hero_stat.name, modifier.delta)
        return string

    @staticmethod
    def randomized_base(item_type: ItemType, name: str, base_stats: List[StatModifierInterval]):
        modifiers = [StatModifier(modifier_interval.hero_stat, random.choice(modifier_interval.interval))
                     for modifier_interval in base_stats]
        return ItemId(item_type, name, modifiers, [])

    @staticmethod
    def randomized_with_affix(item_type: ItemType, name: str, base_stats: List[StatModifierInterval],
                              affix_stats: List[StatModifierInterval]):
        base_stat_modifiers = [StatModifier(modifier_interval.hero_stat, random.choice(modifier_interval.interval))
                               for modifier_interval in base_stats]
        affix_stat_modifiers = [StatModifier(modifier_interval.hero_stat, random.choice(modifier_interval.interval))
                                for modifier_interval in affix_stats]
        return ItemId(item_type, name, base_stat_modifiers, affix_stat_modifiers)

    @staticmethod
    def from_stats_string(item_id: str, item_name: str):
        try:
            parts = item_id.split("~")
            item_type = ItemType[parts[0]]
            base_part = parts[1]
            affix_part = parts[2]
            base_stats = []
            affix_stats = []

            if base_part:
                base_subparts = base_part.split(":")
                for i in range(1, len(base_subparts) - 1, 2):
                    hero_stat: HeroStat = HeroStat[base_subparts[i]]
                    value_str = base_subparts[i + 1]
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)
                    base_stats.append(StatModifier(hero_stat, value))
            if affix_part:
                affix_subparts = affix_part.split(":")
                for i in range(1, len(affix_subparts) - 1, 2):
                    hero_stat: HeroStat = HeroStat[affix_subparts[i]]
                    value_str = affix_subparts[i + 1]
                    try:
                        value = int(value_str)
                    except ValueError:
                        value = float(value_str)
                    affix_stats.append(StatModifier(hero_stat, value))
            return ItemId(item_type, item_name, base_stats, affix_stats)
        except Exception as e:
            raise Exception("Failed to parse item_id '" + item_id + "'", e)

    def __eq__(self, other):
        return isinstance(other, ItemId) and self.stats_string == other.stats_string


class ProjectileType(Enum):
    PLAYER_FIREBALL = 1
    PLAYER_ARCANE_FIRE = 2
    PLAYER_WHIRLWIND = 3
    PLAYER_ENTANGLING_ROOTS = 4
    ENEMY_GOBLIN_WARLOCK = 101
    ENEMY_NECROMANCER = 102
    ENEMY_SKELETON_MAGE = 103
    ENEMY_SKELETON_BOSS = 104


class SoundId(Enum):
    ABILITY_FIREBALL = 1
    ABILITY_WHIRLWIND = 2
    ABILITY_TELEPORT = 3
    ABILITY_ENTANGLING_ROOTS = 4
    ABILITY_CHARGE = 5
    ABILITY_SHIV = 6
    ABILITY_STEALTH = 7
    ABILITY_INFUSE_DAGGER = 8
    ABILITY_DASH = 9
    ABILITY_SLASH = 10
    ABILITY_STOMP_HIT = 11
    ABILITY_BLOODLUST = 12
    ABILITY_ARCANE_FIRE = 13
    ABILITY_SHIV_STEALTHED = 14
    ABILITY_FIREBALL_HIT = 15
    ABILITY_ENTANGLING_ROOTS_HIT = 16
    ABILITY_CHARGE_HIT = 17
    ABILITY_STOMP = 18
    WARP = 40
    CONSUMABLE_POTION = 50
    CONSUMABLE_BUFF = 51
    CONSUMABLE_ACID_BOMB = 52
    EVENT_PLAYER_LEVELED_UP = 100
    EVENT_PICKED_UP = 101
    EVENT_PLAYER_DIED = 102
    EVENT_ENEMY_DIED = 103
    EVENT_PICKED_UP_MONEY = 104
    EVENT_PURCHASED_SOMETHING = 105
    EVENT_PORTAL_ACTIVATED = 106
    EVENT_COMPLETED_QUEST = 107
    EVENT_PICKED_TALENT = 108
    EVENT_SOLD_SOMETHING = 109
    EVENT_SAVED_GAME = 110
    EVENT_ACCEPTED_QUEST = 111
    EVENT_RESET_TALENT = 108
    WARNING = 200
    INVALID_ACTION = 201
    PLAYER_PAIN = 300
    ENEMY_ATTACK_GOBLIN_WARLOCK = 400
    ENEMY_ATTACK = 401
    ENEMY_ATTACK_WAS_BLOCKED = 402
    ENEMY_NECROMANCER_SUMMON = 403
    ENEMY_ATTACK_ICE_WITCH = 404
    ENEMY_ATTACK_NECRO = 405
    ENEMY_NECROMANCER_HEAL = 406
    ENEMY_ATTACK_WAS_DODGED = 407
    MAGIC_DAMAGE_WAS_RESISTED = 409
    ENEMY_ATTACK_SKELETON_MAGE = 410
    ENEMY_SKELETON_MAGE_HEAL = 411
    ENEMY_MAGIC_SKELETON_BOSS = 412
    DEATH_RAT = 500
    DEATH_ZOMBIE = 501
    DEATH_BOSS = 502
    DEATH_GOBLIN = 503
    DEATH_ICE_WITCH = 504
    DEATH_HUMAN = 505
    DEATH_NECRO = 506
    DEATH_SKELETON_MAGE = 507
    UI_ITEM_WAS_MOVED = 600
    UI_START_DRAGGING_ITEM = 601
    UI_ITEM_WAS_DROPPED_ON_GROUND = 602
    UI_TOGGLE = 603
    DIALOG = 700
    FOOTSTEPS = 800


class PortalId(Enum):
    GOBLIN_HIDEOUT_BASE = 1
    GOBLIN_HIDEOUT_REMOTE = 2
    DWARF_CAMP_BASE = 3
    DWARF_CAMP_REMOTE = 4
    GOBLIN_FORTRESS_BASE = 5
    GOBLIN_FORTRESS_REMOTE = 6
    RED_BARON_FORTRESS_BASE = 7
    RED_BARON_FORTRESS_REMOTE = 8
    DEMON_HALL_BASE = 9
    DEMON_HALL_REMOTE = 10


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
    ELIXIR_POWER = 16
    ELIXIR_MAGIC_RESIST = 17
    CONSUMABLE_ACID_BOMB = 18
    ABILITY_FIREBALL = 101
    ABILITY_HEAL = 102
    ABILITY_ARCANE_FIRE = 103
    ABILITY_TELEPORT = 104
    ABILITY_FROST_NOVA = 105
    ABILITY_WHIRLWIND = 106
    ABILITY_ENTANGLING_ROOTS = 107
    ABILITY_SWORD_SLASH = 109
    ABILITY_BLOODLUST = 110
    ABILITY_CHARGE = 111
    ABILITY_STOMP = 112
    ABILITY_SHIV = 113
    ABILITY_STEALTH = 114
    ABILITY_INFUSE_DAGGER = 115
    ABILITY_DASH = 116
    ABILITY_KILL_EVERYTHING = 117
    ITEM_MESSENGERS_HAT = 201
    ITEM_AMULET_OF_MANA = 202
    ITEM_SKULL_STAFF = 203
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
    ITEM_SAPPHIRE = 218
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
    ITEM_HATCHET = 234
    ITEM_ELITE_HELMET = 235
    ITEM_STONE_AMULET = 236
    ITEM_TORN_DOCUMENT = 237
    ITEM_KEY = 238
    ITEM_WOODEN_SWORD = 239
    ITEM_DRUIDS_RING = 240
    ITEM_WARLOCKS_COWL = 241
    ITEM_LICH_ARMOR = 242
    ITEM_WARLORDS_ARMOR = 243
    ITEM_HEALING_WAND = 244
    ITEM_SKULL_SHIELD = 245
    ITEM_THIEFS_MASK = 246
    ITEM_SERPENT_SWORD = 247
    ITEM_WHIP = 248
    ITEM_CLEAVER = 249
    ITEM_DESERT_BLADE = 250
    ITEM_PRACTICE_SWORD = 251
    ITEM_NOVICE_WAND = 252
    ITEM_SORCERESS_ROBE = 253
    ITEM_BLESSED_CHALICE = 254
    ITEM_NECKLACE_OF_SUFFERING = 255
    ITEM_FIRE_WAND = 256
    ITEM_FEATHER_HAT = 257
    ITEM_CANDLE = 258
    ITEM_BRONZE_RING = 259
    ITEM_FIRE_GAUNTLET = 260
    ITEM_SKULL_SWORD = 261
    ITEM_SUN_SHIELD = 262
    ITEM_CORRUPTED_ORB = 263
    ITEM_PORTAL_KEY = 264
    MAP_EDITOR_TRASHCAN = 301
    MAP_EDITOR_RECYCLING = 302
    INVENTORY_TEMPLATE_HELMET = 400
    INVENTORY_TEMPLATE_CHEST = 401
    INVENTORY_TEMPLATE_MAINHAND = 402
    INVENTORY_TEMPLATE_OFFHAND = 403
    INVENTORY_TEMPLATE_NECK = 404
    INVENTORY_TEMPLATE_RING = 405
    TALENT_LIGHT_FOOTED = 500
    TALENT_MOVE_SPEED = 501


# Portraits that are shown in UI (player portrait and dialog portraits)
class PortraitIconSprite(Enum):
    VIKING = 2
    NOMAD = 3
    NINJA = 4
    SORCERER = 5
    YOUNG_SORCERESS = 6
    WARPSTONE_MERCHANT = 7
    CHALLENGE_STARTER = 9
    FROG = 10
    TALENT_MASTER = 11
    HERO_MAGE = 100
    HERO_WARRIOR = 101
    HERO_ROGUE = 102
    HERO_GOD = 103


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
        "If you die, you'll respawn but lose exp points",
        "Use magic statues and warpstones to teleport long distances",
        "Hover over UI elements with the mouse cursor to get more info",
        "Drag inventory items and consumables with the mouse cursor",
        "Equip items by dragging them to the appropriate inventory slot",
        "Choose talents to improve your stats and abilities"
    ]
    return random.choice(hints)


class SceneTransition:
    # scene: AbstractScene
    def __init__(self, scene):
        self.scene = scene


class AbstractScene:

    def on_enter(self):
        pass

    def handle_user_input(self, events: List[Any]) -> Optional[SceneTransition]:
        pass

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:
        pass

    def render(self):
        pass


# These are sent as messages to player. They let buffs and items react to events. One buff might have its
# duration prolonged if an enemy dies for example, and an item might give mana on enemy kills.
class Event:
    pass


class HeroUpgrade:

    def __init__(self, hero_upgrade_id: HeroUpgradeId):
        self._hero_upgrade_id = hero_upgrade_id

    # Override this method for upgrades that need to actively handle events
    def handle_event(self, event: Event, game_state: Any):
        pass

    def get_upgrade_id(self):
        if self._hero_upgrade_id is None:
            raise Exception("hero_upgrade_id is not initialized: " + str(HeroUpgrade))
        return self._hero_upgrade_id


class DialogOptionData:
    def __init__(self, summary: str, action_text: str, action: Optional[Any],
                 ui_icon_sprite: Optional[UiIconSprite] = None, detail_header: Optional[str] = None,
                 detail_body: Optional[str] = None):
        self.summary = summary
        self.action_text = action_text
        self.action = action
        self.ui_icon_sprite = ui_icon_sprite
        self.detail_header = detail_header
        self.detail_body = detail_body


class DialogData:
    def __init__(self, name: str, portrait_icon_sprite: PortraitIconSprite, text_body: str,
                 options: List[DialogOptionData]):
        self.name = name
        self.portrait_icon_sprite = portrait_icon_sprite
        self.text_body = text_body
        self.options = options


class LootTableId(Enum):
    CHEST = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    BOSS_GOBLIN = 100
    BOSS_WARRIOR_KING = 101
    BOSS_SKELETON = 102


class EngineEvent(Enum):
    PLAYER_DIED = 1
    ENEMY_DIED = 2


class AbstractWorldBehavior:

    def on_startup(self, new_hero_was_created: bool):
        pass

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        pass

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        pass
