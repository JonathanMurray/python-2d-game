from typing import Dict, Union, List

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


# TODO Ideally this shouldn't need to be defined here
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
    def __init__(self, icon_sprite: UiIconSprite, mana_cost: int, key_string: str, pygame_key, cooldown: Millis):
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.key_string = key_string
        self.pygame_key = pygame_key
        self.cooldown = cooldown


class EnemyData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, speed: float):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.speed = speed


ENEMIES: Dict[EnemyType, EnemyData] = {}

ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Union[SpriteInitializer, List[SpriteMapInitializer]]]] = {
    Sprite.WALL: {
        Direction.DOWN: SpriteInitializer("resources/graphics/stone_tile.png", (WALL_SIZE[0] - 1, WALL_SIZE[1] - 1))
    }
}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

POTION_ICON_SPRITES: Dict[PotionType, UiIconSprite] = {}

ABILITIES: Dict[AbilityType, AbilityData] = {}

BUFF_TEXTS: Dict[BuffType, str] = {}


def register_enemy_data(enemy_type: EnemyType, enemy_data: EnemyData):
    ENEMIES[enemy_type] = enemy_data


def register_ability_data(ability_type: AbilityType, ability_data: AbilityData):
    ABILITIES[ability_type] = ability_data


def register_ui_icon_sprite_path(sprite: UiIconSprite, file_path: str):
    UI_ICON_SPRITE_PATHS[sprite] = file_path


def register_entity_sprite_initializer(sprite: Sprite, initializer: SpriteInitializer):
    # TODO Support different sprites for different directions
    ENTITY_SPRITE_INITIALIZERS[sprite] = {Direction.DOWN: initializer}


def register_entity_sprite_map(
        sprite: Sprite,
        sprite_sheet: SpriteSheet,
        original_sprite_size: Tuple[int, int],
        scaled_sprite_size: Tuple[int, int],
        indices_by_dir: Dict[Direction, List[Tuple[int, int]]]):
    initializers = {
        direction: [SpriteMapInitializer(sprite_sheet, original_sprite_size, scaled_sprite_size, index)
                    for index in indices_by_dir[direction]]
        for direction in indices_by_dir
    }
    ENTITY_SPRITE_INITIALIZERS[sprite] = {}
    for direction in initializers:
        if len(initializers[direction]) == 0:
            raise Exception("Invalid input: " + str(initializers))
        ENTITY_SPRITE_INITIALIZERS[sprite][direction] = initializers[direction]


def register_buff_text(buff_type: BuffType, text: str):
    BUFF_TEXTS[buff_type] = text


def register_potion_icon_sprite(potion_type: PotionType, ui_icon_sprite: UiIconSprite):
    POTION_ICON_SPRITES[potion_type] = ui_icon_sprite
