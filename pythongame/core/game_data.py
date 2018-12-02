from typing import Dict, List, Optional

# We should probably not load image files in here!
import pygame

from pythongame.core.common import *

WALL_SIZE = (25, 25)


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
    HEALTH_POTION = 1
    MANA_POTION = 2
    SPEED_POTION = 3
    ABILITY_FIREBALL = 4
    HEAL_ABILITY = 5
    AOE_ABILITY = 6
    INVISIBILITY_POTION = 7
    MAGIC_MISSILE = 8
    TELEPORT = 9
    ABILITY_FROST_NOVA = 10


class AbilityData:
    def __init__(self, icon_sprite: UiIconSprite, mana_cost: int, cooldown: Millis):
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.cooldown = cooldown


class UserAbilityKey:
    def __init__(self, key_string: str, pygame_key):
        self.key_string = key_string
        self.pygame_key = pygame_key


class EnemyData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, speed: float):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.speed = speed


ENEMIES: Dict[EnemyType, EnemyData] = {}

_stone_tile_file_name = "resources/graphics/stone_tile.png"
ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Animation]] = {
    Sprite.WALL: {
        Direction.DOWN: Animation(
            [SpriteInitializer(_stone_tile_file_name, (WALL_SIZE[0] - 2, WALL_SIZE[1] - 2))], None, (1, 1))
    }
}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

POTION_ICON_SPRITES: Dict[PotionType, UiIconSprite] = {}

POTION_ENTITY_SPRITES: Dict[PotionType, Sprite] = {}

POTION_NAMES: Dict[PotionType, str] = {}

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


def register_potion_icon_sprite(potion_type: PotionType, ui_icon_sprite: UiIconSprite):
    POTION_ICON_SPRITES[potion_type] = ui_icon_sprite


def register_potion_entity_sprite(potion_type: PotionType, sprite: Sprite):
    POTION_ENTITY_SPRITES[potion_type] = sprite

def register_potion_name(potion_type: PotionType, name: str):
    POTION_NAMES[potion_type] = name