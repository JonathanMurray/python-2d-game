from typing import Dict, List, Optional, Tuple

# We should probably not load image files in here!
import pygame

from pythongame.core.common import *
from pythongame.core.common import UiIconSprite, PortraitIconSprite
from pythongame.core.loot import LootTable

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
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
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


user_ability_keys = [UserAbilityKey("Q", pygame.K_q),
                     UserAbilityKey("W", pygame.K_w),
                     UserAbilityKey("E", pygame.K_e),
                     UserAbilityKey("R", pygame.K_r),
                     UserAbilityKey("T", pygame.K_t)]


class NpcCategory(Enum):
    ENEMY = 1
    PLAYER_SUMMON = 2
    NEUTRAL = 3


class NpcData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float,
                 exp_reward: int, npc_category: NpcCategory, enemy_loot_table: Optional[LootTable],
                 death_sound_id: Optional[SoundId], max_distance_allowed_from_start_position: Optional[int]):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.health_regen = health_regen
        self.speed = speed
        self.exp_reward = exp_reward
        self.npc_category = npc_category
        self.enemy_loot_table: LootTable = enemy_loot_table
        self.death_sound_id: Optional[SoundId] = death_sound_id
        self.max_distance_allowed_from_start_position = max_distance_allowed_from_start_position

    @staticmethod
    def enemy(sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float,
              exp_reward: int, enemy_loot_table: Optional[LootTable], death_sound_id: Optional[SoundId] = None):
        return NpcData(sprite, size, max_health, health_regen, speed, exp_reward, NpcCategory.ENEMY, enemy_loot_table,
                       death_sound_id, None)

    @staticmethod
    def player_summon(sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float):
        return NpcData(sprite, size, max_health, health_regen, speed, 0, NpcCategory.PLAYER_SUMMON, None, None, None)

    @staticmethod
    def neutral(sprite: Sprite, size: Tuple[int, int], speed: float):
        # Neutral NPC's shouldn't wander off from their start location
        max_distance_allowed_from_start_position = 40
        return NpcData(sprite, size, 5, 0, speed, 0, NpcCategory.NEUTRAL, None, None,
                       max_distance_allowed_from_start_position)


class ConsumableCategory(Enum):
    HEALTH = 1
    MANA = 2
    OTHER = 3


class ConsumableData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Optional[Sprite], name: str, description: str,
                 category: ConsumableCategory):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.description = description
        self.category = category


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


class PortalData:
    def __init__(self, starts_enabled: bool, leads_to: Optional[PortalId], sprite: Sprite,
                 entity_size: Tuple[int, int], teleport_delay: Millis):
        self.starts_enabled = starts_enabled
        self.leads_to = leads_to
        self.sprite = sprite
        self.entity_size = entity_size
        self.teleport_delay = teleport_delay


class PlayerLevelBonus:
    def __init__(self, health: int, mana: int):
        self.health = health
        self.mana = mana


class InitialPlayerStateData:
    def __init__(
            self, health: int, mana: int, mana_regen: float, consumable_slots: Dict[int, ConsumableType],
            abilities: List[AbilityType], item_slots: Dict[int, ItemType], new_level_abilities: Dict[int, AbilityType],
            hero_id: HeroId, armor: int, level_bonus: PlayerLevelBonus):
        self.health = health
        self.mana = mana
        self.mana_regen = mana_regen
        self.consumable_slots = consumable_slots
        self.abilities = abilities
        self.item_slots = item_slots
        self.new_level_abilities = new_level_abilities
        self.hero_id = hero_id
        self.armor = armor
        self.level_bonus = level_bonus


class HeroData:
    def __init__(self, sprite: Sprite, portrait_icon_sprite: PortraitIconSprite,
                 initial_player_state: InitialPlayerStateData, entity_speed: float, entity_size: Tuple[int, int]):
        self.sprite = sprite
        self.portrait_icon_sprite = portrait_icon_sprite
        self.initial_player_state = initial_player_state
        self.entity_speed = entity_speed
        self.entity_size = entity_size


NON_PLAYER_CHARACTERS: Dict[NpcType, NpcData] = {}

ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Animation]] = {}

ENTITY_SPRITE_SIZES: Dict[Sprite, Tuple[int, int]] = {}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

PORTRAIT_ICON_SPRITE_PATHS: Dict[PortraitIconSprite, str] = {}

CONSUMABLES: Dict[ConsumableType, ConsumableData] = {}

WALLS: Dict[WallType, WallData] = {}

ITEMS: Dict[ItemType, ItemData] = {}

ABILITIES: Dict[AbilityType, AbilityData] = {}

KEYS_BY_ABILITY_TYPE: Dict[AbilityType, UserAbilityKey] = {}

BUFF_TEXTS: Dict[BuffType, str] = {}

CHANNELING_BUFFS: List[BuffType] = []

PORTALS: Dict[PortalId, PortalData] = {}

HEROES: Dict[HeroId, HeroData] = {}


def register_npc_data(npc_type: NpcType, npc_data: NpcData):
    NON_PLAYER_CHARACTERS[npc_type] = npc_data


def register_wall_data(wall_type: WallType, wall_data: WallData):
    WALLS[wall_type] = wall_data


def register_ability_data(ability_type: AbilityType, ability_data: AbilityData):
    ABILITIES[ability_type] = ability_data


def allocate_input_keys_for_abilities(abilities: List[AbilityType]):
    for i, ability in enumerate(abilities):
        KEYS_BY_ABILITY_TYPE[ability] = user_ability_keys[i]


def register_ui_icon_sprite_path(sprite: UiIconSprite, file_path: str):
    UI_ICON_SPRITE_PATHS[sprite] = file_path


def register_portrait_icon_sprite_path(sprite: PortraitIconSprite, file_path: str):
    PORTRAIT_ICON_SPRITE_PATHS[sprite] = file_path


# Deprecated
def register_entity_sprite_initializer(sprite: Sprite, initializer: SpriteInitializer):
    ENTITY_SPRITE_INITIALIZERS[sprite] = {Direction.DOWN: Animation([initializer], None, (0, 0))}
    ENTITY_SPRITE_SIZES[sprite] = initializer.scaling_size


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
    ENTITY_SPRITE_SIZES[sprite] = scaled_sprite_size


def register_buff_text(buff_type: BuffType, text: str):
    BUFF_TEXTS[buff_type] = text


# Indicates that this buff should be visualized with a "channeling bar" in the UI,
# rather than a decreasing buff bar as other buffs
def register_buff_as_channeling(buff_type: BuffType):
    CHANNELING_BUFFS.append(buff_type)


def register_consumable_data(consumable_type: ConsumableType, data: ConsumableData):
    CONSUMABLES[consumable_type] = data


def register_item_data(item_type: ItemType, item_data: ItemData):
    ITEMS[item_type] = item_data


def register_portal_data(portal_id: PortalId, portal_data: PortalData):
    PORTALS[portal_id] = portal_data


def register_hero_data(hero_id: HeroId, hero_data: HeroData):
    HEROES[hero_id] = hero_data
