from typing import Dict, List, Optional

# We should probably not load image files in here!
import pygame

from pythongame.core.common import *

WALL_SIZE = (25, 25)

ITEM_ENTITY_SIZE = (30, 30)


class SpriteInitializer:
    def __init__(self, image_file_path: str, scaling_size: Tuple[int, int]):
        self.image_file_path = image_file_path
        self.scaling_size = scaling_size


class SpriteSheet(object):
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheet = None

    def _load_sheet(self):
        self.sheet = pygame.image.load(self.file_path).convert_alpha()

    def image_at(self, rectangle: Tuple[int, int, int, int]):
        if self.sheet is None:
            self._load_sheet()

        rect = pygame.Rect(rectangle)
        # noinspection PyArgumentList
        image = pygame.Surface(rect.size).convert()
        destination_in_image = (0, 0)
        image.blit(self.sheet, destination_in_image, rect)
        transparent_color_in_image = (0, 0, 0)
        image.set_colorkey(transparent_color_in_image, pygame.RLEACCEL)
        return image


class SpriteMapInitializer:
    def __init__(self, sprite_sheet: SpriteSheet, original_sprite_size: Tuple[int, int], scaling_size: Tuple[int, int],
                 index_position_within_map: Tuple[int, int]):
        self.sprite_sheet = sprite_sheet
        self.original_sprite_size = original_sprite_size
        self.scaling_size = scaling_size
        self.index_position_within_map = index_position_within_map


class Animation:
    def __init__(
            self,
            sprite_initializers: Optional[List[SpriteInitializer]],
            sprite_map_initializers: Optional[List[SpriteMapInitializer]],
            position_relative_to_entity: Tuple[int, int]):
        self.sprite_initializers = sprite_initializers
        self.sprite_map_initializers = sprite_map_initializers
        self.position_relative_to_entity = position_relative_to_entity


# TODO Ideally this shouldn't need to be defined here
class UiIconSprite(Enum):
    POTION_HEALTH = 1
    POTION_MANA = 2
    POTION_SPEED = 3
    POTION_INVISIBILITY = 4
    ABILITY_FIREBALL = 101
    ABILITY_HEAL = 102
    ABILITY_MAGIC_MISSILE = 103
    ABILITY_TELEPORT = 104
    ABILITY_FROST_NOVA = 105
    ABILITY_WHIRLWIND = 106
    ABILITY_ENTANGLING_ROOTS = 107
    ITEM_WINGED_BOOTS = 201
    ITEM_AMULET_OF_MANA = 202
    ITEM_SWORD_OF_LEECHING = 203
    ITEM_ROD_OF_LIGHTNING = 204


class AbilityData:
    def __init__(self, name: str, icon_sprite: UiIconSprite, mana_cost: int, cooldown: Millis, description: str):
        self.name = name
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.description = description


class UserAbilityKey:
    def __init__(self, key_string: str, pygame_key):
        self.key_string = key_string
        self.pygame_key = pygame_key


class EnemyData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.health_regen = health_regen
        self.speed = speed


class PotionData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Optional[Sprite], name: str):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, name: str, description: str):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.description = description


ENEMIES: Dict[EnemyType, EnemyData] = {}

_stone_tile_file_name = "resources/graphics/stone_tile.png"
ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Animation]] = {
    Sprite.WALL: {
        Direction.DOWN: Animation(
            [SpriteInitializer(_stone_tile_file_name, (WALL_SIZE[0] - 2, WALL_SIZE[1] - 2))], None, (1, 1))
    }
}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

POTIONS: Dict[PotionType, PotionData] = {}

ITEMS: Dict[ItemType, ItemData] = {}

ABILITIES: Dict[AbilityType, AbilityData] = {}

USER_ABILITY_KEYS: Dict[AbilityType, UserAbilityKey] = {}

BUFF_TEXTS: Dict[BuffType, str] = {}


def register_enemy_data(enemy_type: EnemyType, enemy_data: EnemyData):
    ENEMIES[enemy_type] = enemy_data


def register_ability_data(ability_type: AbilityType, ability_data: AbilityData):
    ABILITIES[ability_type] = ability_data


def register_user_ability_key(ability_type: AbilityType, user_ability_key: UserAbilityKey):
    USER_ABILITY_KEYS[ability_type] = user_ability_key


def register_ui_icon_sprite_path(sprite: UiIconSprite, file_path: str):
    UI_ICON_SPRITE_PATHS[sprite] = file_path


# Deprecated
def register_entity_sprite_initializer(sprite: Sprite, initializer: SpriteInitializer):
    ENTITY_SPRITE_INITIALIZERS[sprite] = {Direction.DOWN: Animation([initializer], None, (0, 0))}


def register_entity_sprite_map(
        sprite: Sprite,
        sprite_sheet: SpriteSheet,
        original_sprite_size: Tuple[int, int],
        scaled_sprite_size: Tuple[int, int],
        indices_by_dir: Dict[Direction, List[Tuple[int, int]]],
        position_relative_to_entity: Tuple[int, int]):
    initializers: Dict[Direction: SpriteMapInitializer] = {
        direction: [SpriteMapInitializer(sprite_sheet, original_sprite_size, scaled_sprite_size, index)
                    for index in indices_by_dir[direction]]
        for direction in indices_by_dir
    }
    ENTITY_SPRITE_INITIALIZERS[sprite] = {}
    for direction in initializers:
        if len(initializers[direction]) == 0:
            raise Exception("Invalid input: " + str(initializers))
        ENTITY_SPRITE_INITIALIZERS[sprite][direction] = Animation(
            None, initializers[direction], position_relative_to_entity)


def register_buff_text(buff_type: BuffType, text: str):
    BUFF_TEXTS[buff_type] = text


def register_potion_data(potion_type: PotionType, potion_data: PotionData):
    POTIONS[potion_type] = potion_data


def register_item_data(item_type: ItemType, item_data: ItemData):
    ITEMS[item_type] = item_data
