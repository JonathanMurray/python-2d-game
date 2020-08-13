from typing import Set, Dict

from pythongame.core.common import *
from pythongame.core.common import UiIconSprite, PortraitIconSprite
from pythongame.core.talents import TalentsConfig
from pythongame.core.view.image_loading import SpriteInitializer, SpriteSheet, SpriteMapInitializer, Animation

POTION_ENTITY_SIZE = (30, 30)


class NpcCategory(Enum):
    ENEMY = 1
    PLAYER_SUMMON = 2
    NEUTRAL = 3


class NpcData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float,
                 exp_reward: int, npc_category: NpcCategory, enemy_loot_table: Optional[LootTableId],
                 death_sound_id: Optional[SoundId], max_distance_allowed_from_start_position: Optional[int],
                 is_boss=False):
        self.sprite = sprite
        self.size = size
        self.max_health = max_health
        self.health_regen = health_regen
        self.speed = speed
        self.exp_reward = exp_reward
        self.npc_category = npc_category
        self.enemy_loot_table: LootTableId = enemy_loot_table
        self.death_sound_id: Optional[SoundId] = death_sound_id
        self.max_distance_allowed_from_start_position = max_distance_allowed_from_start_position
        self.is_boss = is_boss

    @staticmethod
    def enemy(sprite: Sprite, size: Tuple[int, int], max_health: int, health_regen: float, speed: float,
              exp_reward: int, enemy_loot_table: Optional[LootTableId], death_sound_id: Optional[SoundId] = None,
              is_boss: bool = False):
        return NpcData(sprite, size, max_health, health_regen, speed, exp_reward, NpcCategory.ENEMY, enemy_loot_table,
                       death_sound_id, None, is_boss=is_boss)

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
                 category: ConsumableCategory, sound: SoundId):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.description = description
        self.category = category
        self.sound = sound


class WallData:
    def __init__(self, sprite: Sprite, size: Tuple[int, int]):
        self.sprite = sprite
        self.size = size


class PortalData:
    def __init__(self, starts_enabled: bool, leads_to: Optional[PortalId], sprite: Sprite,
                 entity_size: Tuple[int, int], teleport_delay: Millis, destination_name: str):
        self.starts_enabled = starts_enabled
        self.leads_to = leads_to
        self.sprite = sprite
        self.entity_size = entity_size
        # TODO remove teleport_delay (constant value is always used)
        self.teleport_delay = teleport_delay
        self.destination_name = destination_name


class PlayerLevelBonus:
    def __init__(self, health: int, mana: int, armor: float):
        self.health = health
        self.mana = mana
        self.armor = armor


class InitialPlayerStateData:
    def __init__(
            self, health: int, mana: int, mana_regen: float, consumable_slots: Dict[int, List[ConsumableType]],
            abilities: List[AbilityType], new_level_abilities: Dict[int, AbilityType], hero_id: HeroId, armor: int,
            dodge_chance: float, level_bonus: PlayerLevelBonus, talents_state: TalentsConfig, block_chance: float,
            starting_items: List[ItemId]):
        self.health = health
        self.mana = mana
        self.mana_regen = mana_regen
        self.consumable_slots = consumable_slots
        self.abilities = abilities
        self.new_level_abilities = new_level_abilities
        self.hero_id = hero_id
        self.armor = armor
        self.dodge_chance = dodge_chance
        self.level_bonus = level_bonus
        self.talents_state = talents_state
        self.block_chance = block_chance
        self.starting_items = starting_items


class HeroData:
    def __init__(self, sprite: Sprite, portrait_icon_sprite: PortraitIconSprite,
                 initial_player_state: InitialPlayerStateData, entity_speed: float, entity_size: Tuple[int, int],
                 description: str):
        self.sprite = sprite
        self.portrait_icon_sprite = portrait_icon_sprite
        self.initial_player_state = initial_player_state
        self.entity_speed = entity_speed
        self.entity_size = entity_size
        self.description = description


NON_PLAYER_CHARACTERS: Dict[NpcType, NpcData] = {}

ENTITY_SPRITE_INITIALIZERS: Dict[Sprite, Dict[Direction, Animation]] = {}

ENTITY_SPRITE_SIZES: Dict[Sprite, Tuple[int, int]] = {}

UI_ICON_SPRITE_PATHS: Dict[UiIconSprite, str] = {}

PORTRAIT_ICON_SPRITE_PATHS: Dict[PortraitIconSprite, str] = {}

# TODO use methods instead of accessing this directly
CONSUMABLES: Dict[ConsumableType, ConsumableData] = {}

WALLS: Dict[WallType, WallData] = {}

consumable_data_by_type: Dict[ConsumableType, ConsumableData] = {}
consumable_types_grouped_by_level: Dict[int, Set[ConsumableType]] = {}
consumable_levels: Dict[ConsumableType, int] = {}

BUFF_TEXTS: Dict[BuffType, str] = {}

CHANNELING_BUFFS: List[BuffType] = []

PORTALS: Dict[PortalId, PortalData] = {}

HEROES: Dict[HeroId, HeroData] = {}


def register_npc_data(npc_type: NpcType, npc_data: NpcData):
    NON_PLAYER_CHARACTERS[npc_type] = npc_data


def register_wall_data(wall_type: WallType, wall_data: WallData):
    WALLS[wall_type] = wall_data


def register_ui_icon_sprite_path(sprite: UiIconSprite, file_path: str):
    UI_ICON_SPRITE_PATHS[sprite] = file_path


def register_portrait_icon_sprite_path(sprite: PortraitIconSprite, file_path: str):
    PORTRAIT_ICON_SPRITE_PATHS[sprite] = file_path


def register_entity_sprite_initializer(sprite: Sprite, initializer: SpriteInitializer,
                                       position_relative_to_entity: Tuple[int, int] = (0, 0)):
    ENTITY_SPRITE_INITIALIZERS[sprite] = {Direction.DOWN: Animation([initializer], None, position_relative_to_entity)}
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


def register_consumable_level(consumable_type: ConsumableType, level: int):
    consumable_types = consumable_types_grouped_by_level.setdefault(level, set())
    consumable_types.add(consumable_type)
    consumable_levels[consumable_type] = level


def get_consumables_with_level(level: int) -> List[ConsumableType]:
    return list(consumable_types_grouped_by_level.get(level, set()))


def get_optional_consumable_level(consumable_type: ConsumableType) -> Optional[int]:
    return consumable_levels.get(consumable_type, None)


def register_portal_data(portal_id: PortalId, portal_data: PortalData):
    PORTALS[portal_id] = portal_data


def register_hero_data(hero_id: HeroId, hero_data: HeroData):
    HEROES[hero_id] = hero_data
