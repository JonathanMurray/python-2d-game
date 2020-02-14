from typing import Set, Dict

# We should probably not load image files in here!
import pygame

from pythongame.core.common import *
from pythongame.core.common import UiIconSprite, PortraitIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.talents import TalentsConfig
from pythongame.core.view.image_loading import SpriteInitializer, SpriteSheet, SpriteMapInitializer, Animation

ITEM_ENTITY_SIZE = (30, 30)
POTION_ENTITY_SIZE = (30, 30)


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

    def __repr__(self):
        return "(" + self.key_string + ", " + str(self.pygame_key) + ")"


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


class ItemData:
    def __init__(self, icon_sprite: UiIconSprite, entity_sprite: Sprite, name: str, custom_description_lines: List[str],
                 stats: List[StatModifierInterval],
                 item_equipment_category: Optional[ItemEquipmentCategory] = None):
        self.icon_sprite = icon_sprite
        self.entity_sprite = entity_sprite
        self.name = name
        self.custom_description_lines: List[str] = custom_description_lines
        self.stats = stats
        self.item_equipment_category = item_equipment_category  # If category is None, the item can't be equipped

    def __repr__(self):
        return "ItemData(%s)" % self.name


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

item_data_by_type: Dict[ItemType, ItemData] = {}

item_types_grouped_by_level: Dict[int, Set[ItemType]] = {}

item_levels: Dict[ItemType, int] = {}

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
    KEYS_BY_ABILITY_TYPE.clear()
    for i, ability in enumerate(abilities):
        KEYS_BY_ABILITY_TYPE[ability] = user_ability_keys[i]


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


def register_item_data(item_type: ItemType, item_data: ItemData):
    item_data_by_type[item_type] = item_data


def get_item_data(item_id: ItemId) -> ItemData:
    item_type = item_type_from_id(item_id)
    return item_data_by_type[item_type]


def get_item_data_by_type(item_type: ItemType) -> ItemData:
    return item_data_by_type[item_type]


def randomized_item_id(item_type: ItemType) -> ItemId:
    data = get_item_data_by_type(item_type)
    return ItemId(ItemIdObj.randomized(item_type, data.stats).id_string)


def register_item_level(item_type: ItemType, item_level: int):
    item_types = item_types_grouped_by_level.setdefault(item_level, set())
    item_types.add(item_type)
    item_levels[item_type] = item_level


def get_items_with_level(item_level: int) -> List[ItemType]:
    return list(item_types_grouped_by_level.get(item_level, set()))


def get_items_within_levels(min_level: int, max_level: int) -> List[ItemType]:
    items = []
    for level in range(min_level, max_level + 1):
        items += get_items_with_level(level)
    return items


def get_optional_item_level(item_type: ItemType) -> Optional[int]:
    return item_levels.get(item_type, None)


def register_portal_data(portal_id: PortalId, portal_data: PortalData):
    PORTALS[portal_id] = portal_data


def register_hero_data(hero_id: HeroId, hero_data: HeroData):
    HEROES[hero_id] = hero_data


def get_items_with_category(category: Optional[ItemEquipmentCategory]) -> List[Tuple[ItemType, ItemData]]:
    return [(item_type, item_data)
            for (item_type, item_data) in item_data_by_type.items()
            if item_data.item_equipment_category == category]
