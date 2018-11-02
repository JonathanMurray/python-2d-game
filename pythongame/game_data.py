from typing import Tuple

import pygame

from pythongame.common import *

PLAYER_ENTITY_SIZE = (60, 60)
ENEMY_ENTITY_SIZE = (28, 28)
ENEMY_2_ENTITY_SIZE = (60, 60)
ENEMY_MAGE_ENTITY_SIZE = (60, 60)
ENEMY_BERSERKER_SIZE = (50, 50)
ATTACK_PROJECTILE_SIZE = (25, 25)
MAGIC_MISSILE_PROJECTILE_SIZE = (30, 30)
ENEMY_PROJECTILE_SIZE = (50, 50)
AOE_PROJECTILE_SIZE = (110, 110)
POTION_ENTITY_SIZE = (30, 30)


class SpriteInitializer:
    def __init__(self, image_file_path: str, scaling_size: Tuple[int, int]):
        self.image_file_path = image_file_path
        self.scaling_size = scaling_size


class UiIconSprite(Enum):
    HEALTH_POTION = 1
    MANA_POTION = 2
    SPEED_POTION = 3
    ATTACK_ABILITY = 4
    HEAL_ABILITY = 5
    AOE_ABILITY = 6
    INVISIBILITY_POTION = 7
    MAGIC_MISSILE = 8
    TELEPORT = 9


class AbilityData:
    def __init__(self, icon_sprite: UiIconSprite, mana_cost: int, key_string: str, pygame_key):
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.key_string = key_string
        self.pygame_key = pygame_key


ENTITY_SPRITE_INITIALIZERS = {
    Sprite.PLAYER: SpriteInitializer("resources/player.png", PLAYER_ENTITY_SIZE),
    Sprite.ENEMY: SpriteInitializer("resources/enemy.png", ENEMY_ENTITY_SIZE),
    Sprite.ENEMY_2: SpriteInitializer("resources/enemy2.png", ENEMY_2_ENTITY_SIZE),
    Sprite.ENEMY_MAGE: SpriteInitializer("resources/enemy_mage.png", ENEMY_MAGE_ENTITY_SIZE),
    Sprite.ENEMY_BERSERKER: SpriteInitializer("resources/orc_berserker.png", ENEMY_BERSERKER_SIZE),
    Sprite.FIREBALL: SpriteInitializer("resources/fireball.png", ATTACK_PROJECTILE_SIZE),
    Sprite.MAGIC_MISSILE: SpriteInitializer("resources/magic_missile.png", MAGIC_MISSILE_PROJECTILE_SIZE),
    Sprite.WHIRLWIND: SpriteInitializer("resources/whirlwind.png", AOE_PROJECTILE_SIZE),
    Sprite.HEALTH_POTION: SpriteInitializer("resources/ui_health_potion.png", POTION_ENTITY_SIZE),
    Sprite.POISONBALL: SpriteInitializer("resources/poisonball.png", ENEMY_PROJECTILE_SIZE),
}

UI_ICON_SPRITE_PATHS = {
    UiIconSprite.HEALTH_POTION: "resources/ui_health_potion.png",
    UiIconSprite.MANA_POTION: "resources/ui_mana_potion.png",
    UiIconSprite.SPEED_POTION: "resources/white_potion.gif",
    UiIconSprite.INVISIBILITY_POTION: "resources/invis_potion.png",
    UiIconSprite.ATTACK_ABILITY: "resources/fireball.png",
    UiIconSprite.HEAL_ABILITY: "resources/heal_ability.png",
    UiIconSprite.AOE_ABILITY: "resources/whirlwind.png",
    UiIconSprite.MAGIC_MISSILE: "resources/magic_missile.png",
    UiIconSprite.TELEPORT: "resources/teleport_icon.png",
}

POTION_ICON_SPRITES = {
    PotionType.HEALTH: UiIconSprite.HEALTH_POTION,
    PotionType.MANA: UiIconSprite.MANA_POTION,
    PotionType.SPEED: UiIconSprite.SPEED_POTION,
    PotionType.INVISIBILITY: UiIconSprite.INVISIBILITY_POTION
}

ABILITIES = {
    AbilityType.ATTACK: AbilityData(UiIconSprite.ATTACK_ABILITY, 3, "Q", pygame.K_q),
    AbilityType.HEAL: AbilityData(UiIconSprite.HEAL_ABILITY, 10, "W", pygame.K_w),
    AbilityType.AOE_ATTACK: AbilityData(UiIconSprite.AOE_ABILITY, 5, "E", pygame.K_e),
    AbilityType.CHANNEL_ATTACK: AbilityData(UiIconSprite.MAGIC_MISSILE, 12, "R", pygame.K_r),
    AbilityType.TELEPORT: AbilityData(UiIconSprite.TELEPORT, 2, "T", pygame.K_t),
}

BUFF_TEXTS = {
    BuffType.DAMAGE_OVER_TIME: "Poison",
    BuffType.INCREASED_MOVE_SPEED: "Speed",
    BuffType.HEALING_OVER_TIME: "Healing",
    BuffType.INVISIBILITY: "Invisibility",
    BuffType.CHANNELING_MAGIC_MISSILES: "Channeling"
}
