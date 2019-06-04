from typing import Dict, List, Optional

# We should probably not load image files in here!
import pygame

from pythongame.core.common import *

ITEM_ENTITY_SIZE = (30, 30)
POTION_ENTITY_SIZE = (30, 30)


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
    POTION_HEALTH_LESSER = 1
    POTION_HEALTH = 2
    POTION_MANA_LESSER = 3
    POTION_MANA = 4
    POTION_SPEED = 11
    POTION_INVISIBILITY = 12
    POTION_SCROLL_ABILITY_SUMMON = 13
    ABILITY_FIREBALL = 101
    ABILITY_HEAL = 102
    ABILITY_MAGIC_MISSILE = 103
    ABILITY_TELEPORT = 104
    ABILITY_FROST_NOVA = 105
    ABILITY_WHIRLWIND = 106
    ABILITY_ENTANGLING_ROOTS = 107
    ABILITY_SUMMON = 108
    ITEM_WINGED_BOOTS = 201
    ITEM_AMULET_OF_MANA = 202
    ITEM_SWORD_OF_LEECHING = 203
    ITEM_ROD_OF_LIGHTNING = 204
    ITEM_SOLDIERS_HELMET = 205
    ITEM_BLESSED_SHIELD = 206
    ITEM_STAFF_OF_FIRE = 207
    MAP_EDITOR_TRASHCAN = 301
    MAP_EDITOR_RECYCLING = 302


# Portraits that are shown in UI (player portrait and dialog portraits)
class PortraitIconSprite(Enum):
    PLAYER = 1
    VIKING = 2
    NOMAD = 3


class AbilityData:
    def __init__(self, name: str, icon_sprite: UiIconSprite, mana_cost: int, cooldown: Millis, description: str,
                 sound_id: Optional[SoundId]):
        self.name = name
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.description = description
        self.sound_id = sound_id


class UserAbilityKey:
    def __init__(self, key_string: str, pygame_key):
        self.key_string = key_string
        self.pygame_key = pygame_key


class NpcData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float,
                 exp_reward: int, is_enemy: bool, is_neutral: bool, dialog: Optional[str],
                 portrait_icon_sprite: Optional[PortraitIconSprite]):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.health_regen = health_regen
        self.speed = speed
        self.exp_reward = exp_reward
        self.is_enemy = is_enemy
        self.is_neutral = is_neutral  # a neutral NPC can't take damage from enemies or player. It may have dialog.
        self.dialog: Optional[str] = dialog
        self.portrait_icon_sprite: Optional[PortraitIconSprite] = portrait_icon_sprite


class ConsumableData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Optional[Sprite], name: str, description: str):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.description = description


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, name: str, description: str):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.description = description


class WallData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int]):
        self.sprite = sprite
        self.size = size


NON_PLAYER_CHARACTERS: Dict[NpcType, NpcData] = {}

ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Animation]] = {}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

PORTRAIT_ICON_SPRITE_PATHS: Dict[PortraitIconSprite, str] = {}

CONSUMABLES: Dict[ConsumableType, ConsumableData] = {}

WALLS: Dict[WallType, WallData] = {}

ITEMS: Dict[ItemType, ItemData] = {}

ABILITIES: Dict[AbilityType, AbilityData] = {}

USER_ABILITY_KEYS: Dict[AbilityType, UserAbilityKey] = {}

BUFF_TEXTS: Dict[BuffType, str] = {}


def register_npc_data(npc_type: NpcType, npc_data: NpcData):
    NON_PLAYER_CHARACTERS[npc_type] = npc_data


def register_wall_data(wall_type: WallType, wall_data: WallData):
    WALLS[wall_type] = wall_data


def register_ability_data(ability_type: AbilityType, ability_data: AbilityData):
    ABILITIES[ability_type] = ability_data


def register_user_ability_key(ability_type: AbilityType, user_ability_key: UserAbilityKey):
    USER_ABILITY_KEYS[ability_type] = user_ability_key


def register_ui_icon_sprite_path(sprite: UiIconSprite, file_path: str):
    UI_ICON_SPRITE_PATHS[sprite] = file_path


def register_portrait_icon_sprite_path(sprite: PortraitIconSprite, file_path: str):
    PORTRAIT_ICON_SPRITE_PATHS[sprite] = file_path


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


def register_consumable_data(consumable_type: ConsumableType, data: ConsumableData):
    CONSUMABLES[consumable_type] = data


def register_item_data(item_type: ItemType, item_data: ItemData):
    ITEMS[item_type] = item_data
