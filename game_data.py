import pygame

from common import *

PLAYER_ENTITY_SIZE = (60, 60)
ENEMY_ENTITY_SIZE = (30, 30)
ENEMY_2_ENTITY_SIZE = (60, 60)

ATTACK_PROJECTILE_SIZE = (25, 25)
AOE_PROJECTILE_SIZE = (110, 110)


class SpriteInitializer:
    def __init__(self, image_file_path, scaling_size):
        self.image_file_path = image_file_path
        self.scaling_size = scaling_size


ENTITY_SPRITE_INITIALIZERS = {
    Sprite.PLAYER: SpriteInitializer("resources/player.png", PLAYER_ENTITY_SIZE),
    Sprite.ENEMY: SpriteInitializer("resources/enemy.png", ENEMY_ENTITY_SIZE),
    Sprite.ENEMY_2: SpriteInitializer("resources/enemy2.png", ENEMY_2_ENTITY_SIZE),
    Sprite.FIREBALL: SpriteInitializer("resources/fireball.png", ATTACK_PROJECTILE_SIZE),
    Sprite.WHIRLWIND: SpriteInitializer("resources/whirlwind.png", AOE_PROJECTILE_SIZE)
}

UI_ICON_SPRITE_PATHS = {
    UiIconSprite.HEALTH_POTION: "resources/ui_health_potion.png",
    UiIconSprite.MANA_POTION: "resources/ui_mana_potion.png",
    UiIconSprite.SPEED_POTION: "resources/white_potion.gif",
    UiIconSprite.ATTACK_ABILITY: "resources/fireball.png",
    UiIconSprite.HEAL_ABILITY: "resources/heal_ability.png",
    UiIconSprite.AOE_ABILITY: "resources/whirlwind.png"
}

POTION_ICON_SPRITES = {
    PotionType.HEALTH: UiIconSprite.HEALTH_POTION,
    PotionType.MANA: UiIconSprite.MANA_POTION,
    PotionType.SPEED: UiIconSprite.SPEED_POTION
}


class AbilityData:
    def __init__(self, icon_sprite, mana_cost, key_string, pygame_key):
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.key_string = key_string
        self.pygame_key = pygame_key


ABILITIES = {
    AbilityType.ATTACK: AbilityData(UiIconSprite.ATTACK_ABILITY, 3, "Q", pygame.K_q),
    AbilityType.HEAL: AbilityData(UiIconSprite.HEAL_ABILITY, 10, "W", pygame.K_w),
    AbilityType.AOE_ATTACK: AbilityData(UiIconSprite.AOE_ABILITY, 5, "E", pygame.K_e)
}

BUFF_TEXTS = {
    BuffType.DAMAGE_OVER_TIME: "Poison",
    BuffType.INCREASED_MOVE_SPEED: "Speed",
    BuffType.HEALING_OVER_TIME: "Healing"
}
