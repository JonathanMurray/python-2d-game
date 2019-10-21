from typing import Tuple

from pythongame.core.common import NpcType, Direction, Sprite, ItemType, ConsumableType, WallType, PortalId, HeroId
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, ITEM_ENTITY_SIZE, ITEMS, CONSUMABLES, POTION_ENTITY_SIZE, \
    WALLS, PORTALS, HEROES, NpcData
from pythongame.core.game_state import WorldEntity, NonPlayerCharacter, MoneyPileOnGround, ItemOnGround, \
    ConsumableOnGround, Portal, Wall, DecorationEntity, PlayerState, HealthOrManaResource, WarpPoint, Chest
from pythongame.core.item_inventory import ItemInventory, ItemInventorySlot, ItemEquipmentCategory
from pythongame.core.math import get_position_from_center_position
from pythongame.core.npc_behaviors import create_npc_mind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.enemy_chest import CHEST_ENTITY_SIZE, CHEST_LOOT

# TODO handle this (global path finder) in a better way!
global_path_finder: GlobalPathFinder = None


def set_global_path_finder(_global_path_finder: GlobalPathFinder):
    global global_path_finder
    global_path_finder = _global_path_finder


def create_npc(npc_type: NpcType, pos: Tuple[int, int]) -> NonPlayerCharacter:
    data: NpcData = NON_PLAYER_CHARACTERS[npc_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    npc_mind = create_npc_mind(npc_type, global_path_finder)
    health_resource = HealthOrManaResource(data.max_health, data.health_regen)
    return NonPlayerCharacter(npc_type, entity, health_resource, npc_mind,
                              data.npc_category, data.enemy_loot_table, data.death_sound_id,
                              data.max_distance_allowed_from_start_position)


def create_money_pile_on_ground(amount: int, pos: Tuple[int, int]) -> MoneyPileOnGround:
    if amount == 1:
        sprite = Sprite.COINS_1
    elif amount == 2:
        sprite = Sprite.COINS_2
    else:
        sprite = Sprite.COINS_5
    return MoneyPileOnGround(WorldEntity(pos, ITEM_ENTITY_SIZE, sprite), amount)


def create_item_on_ground(item_type: ItemType, pos: Tuple[int, int]) -> ItemOnGround:
    entity = WorldEntity(pos, ITEM_ENTITY_SIZE, ITEMS[item_type].entity_sprite)
    entity.view_z = 1  # It should be rendered below all other entities
    return ItemOnGround(entity, item_type)


def create_consumable_on_ground(consumable_type: ConsumableType, pos: Tuple[int, int]) -> ConsumableOnGround:
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, CONSUMABLES[consumable_type].entity_sprite)
    entity.view_z = 1  # It should be rendered below all other entities
    return ConsumableOnGround(entity, consumable_type)


def create_portal(portal_id: PortalId, pos: Tuple[int, int]) -> Portal:
    data = PORTALS[portal_id]
    return Portal(WorldEntity(pos, data.entity_size, data.sprite), portal_id, data.starts_enabled, data.leads_to)


def create_chest(pos: Tuple[int, int]) -> Chest:
    # TODO Allow for other loot in chests (Currently all chests are equal)
    return Chest(WorldEntity(pos, CHEST_ENTITY_SIZE, Sprite.CHEST), CHEST_LOOT)


def create_wall(wall_type: WallType, pos: Tuple[int, int]) -> Wall:
    entity = WorldEntity(pos, WALLS[wall_type].size, WALLS[wall_type].sprite)
    return Wall(wall_type, entity)


def create_hero_world_entity(hero_id: HeroId, pos: Tuple[int, int]) -> WorldEntity:
    data = HEROES[hero_id]
    return WorldEntity(pos, data.entity_size, data.sprite, Direction.RIGHT, data.entity_speed)


def create_decoration_entity(pos: Tuple[int, int], sprite: Sprite) -> DecorationEntity:
    return DecorationEntity(pos, sprite)


def create_player_state(hero_id: HeroId) -> PlayerState:
    data = HEROES[hero_id].initial_player_state
    consumable_inventory = ConsumableInventory(data.consumable_slots)
    item_slots = [
        ItemInventorySlot(None, ItemEquipmentCategory.NECK),
        ItemInventorySlot(None, ItemEquipmentCategory.HEAD),
        ItemInventorySlot(None, ItemEquipmentCategory.RING),
        ItemInventorySlot(None, ItemEquipmentCategory.MAIN_HAND),
        ItemInventorySlot(None, ItemEquipmentCategory.CHEST),
        ItemInventorySlot(None, ItemEquipmentCategory.OFF_HAND),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None)
    ]
    item_inventory = ItemInventory(item_slots)
    health_resource = HealthOrManaResource(data.health, 0)
    mana_resource = HealthOrManaResource(data.mana, data.mana_regen)
    return PlayerState(
        health_resource, mana_resource, consumable_inventory, data.abilities, item_inventory, data.new_level_abilities,
        data.hero_id, data.armor, data.level_bonus, data.talents_state)


def create_warp_point(center_pos: Tuple[int, int], size: Tuple[int, int]) -> WarpPoint:
    entity = WorldEntity(get_position_from_center_position(center_pos, size), size, Sprite.WARP_POINT)
    entity.visible = False  # Warp points start out invisible and are later made visible
    return WarpPoint(entity)
