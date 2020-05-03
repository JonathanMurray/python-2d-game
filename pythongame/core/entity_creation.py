from typing import Tuple, Dict

from pythongame.core.common import NpcType, Direction, Sprite, ConsumableType, WallType, PortalId, HeroId, \
    ItemId, LootTableId
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, CONSUMABLES, POTION_ENTITY_SIZE, \
    WALLS, PORTALS, HEROES, NpcData
from pythongame.core.game_state import NonPlayerCharacter, MoneyPileOnGround, ItemOnGround, \
    ConsumableOnGround, Portal, Wall, DecorationEntity, PlayerState, WarpPoint, Chest, Shrine, \
    DungeonEntrance
from pythongame.core.global_path_finder import get_global_path_finder
from pythongame.core.health_and_mana import HealthOrManaResource
from pythongame.core.item_data import get_item_data_by_type, ITEM_ENTITY_SIZE
from pythongame.core.item_inventory import ItemInventory, ItemInventorySlot, ItemEquipmentCategory
from pythongame.core.math import get_position_from_center_position
from pythongame.core.npc_behaviors import create_npc_mind
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.chests import CHEST_ENTITY_SIZE
from pythongame.game_data.dungeon_entrances import DUNGEON_ENTRANCE_ENTITY_SIZE
from pythongame.game_data.shrines import SHRINE_ENTITY_SIZE


def create_npc(npc_type: NpcType, pos: Tuple[int, int]) -> NonPlayerCharacter:
    data: NpcData = NON_PLAYER_CHARACTERS[npc_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    # TODO is this global pathfinder a problem for handling dungeons that exist in parallel with the main map?
    global_path_finder = get_global_path_finder()
    npc_mind = create_npc_mind(npc_type, global_path_finder)
    health_resource = HealthOrManaResource(data.max_health, data.health_regen)
    return NonPlayerCharacter(npc_type, entity, health_resource, npc_mind,
                              data.npc_category, data.enemy_loot_table, data.death_sound_id,
                              data.max_distance_allowed_from_start_position, is_boss=data.is_boss)


def create_money_pile_on_ground(amount: int, pos: Tuple[int, int]) -> MoneyPileOnGround:
    if amount == 1:
        sprite = Sprite.COINS_1
    elif amount == 2:
        sprite = Sprite.COINS_2
    else:
        sprite = Sprite.COINS_5
    return MoneyPileOnGround(WorldEntity(pos, ITEM_ENTITY_SIZE, sprite), amount)


def create_item_on_ground(item_id: ItemId, pos: Tuple[int, int]) -> ItemOnGround:
    item_type = item_id.item_type
    entity = WorldEntity(pos, ITEM_ENTITY_SIZE, get_item_data_by_type(item_type).entity_sprite)
    entity.view_z = 1  # It should be rendered below all other entities
    return ItemOnGround(entity, item_id)


def create_consumable_on_ground(consumable_type: ConsumableType, pos: Tuple[int, int]) -> ConsumableOnGround:
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, CONSUMABLES[consumable_type].entity_sprite)
    entity.view_z = 1  # It should be rendered below all other entities
    return ConsumableOnGround(entity, consumable_type)


def create_portal(portal_id: PortalId, pos: Tuple[int, int]) -> Portal:
    data = PORTALS[portal_id]
    return Portal(WorldEntity(pos, data.entity_size, data.sprite), portal_id, data.starts_enabled, data.leads_to)


def create_chest(pos: Tuple[int, int]) -> Chest:
    # TODO Allow for other loot in chests (Currently all chests are equal)
    return Chest(WorldEntity(pos, CHEST_ENTITY_SIZE, Sprite.CHEST), LootTableId.CHEST)


def create_shrine(pos: Tuple[int, int]) -> Shrine:
    return Shrine(WorldEntity(pos, SHRINE_ENTITY_SIZE, Sprite.SHRINE), False)


def create_dungeon_entrance(pos: Tuple[int, int]) -> DungeonEntrance:
    return DungeonEntrance(WorldEntity(pos, DUNGEON_ENTRANCE_ENTITY_SIZE, Sprite.DUNGEON_ENTRANCE))


def create_wall(wall_type: WallType, pos: Tuple[int, int]) -> Wall:
    entity = WorldEntity(pos, WALLS[wall_type].size, WALLS[wall_type].sprite)
    return Wall(wall_type, entity)


def create_hero_world_entity(hero_id: HeroId, pos: Tuple[int, int]) -> WorldEntity:
    data = HEROES[hero_id]
    return WorldEntity(pos, data.entity_size, data.sprite, Direction.RIGHT, data.entity_speed)


def create_decoration_entity(pos: Tuple[int, int], sprite: Sprite) -> DecorationEntity:
    return DecorationEntity(pos, sprite)


def create_player_state_as_initial(hero_id: HeroId, enabled_portals: Dict[PortalId, Sprite]) -> PlayerState:
    # Note: All mutable types should be cloned before being given to game_state
    data = HEROES[hero_id].initial_player_state
    consumable_slots = {}
    for slot_number in data.consumable_slots:
        consumable_slots[slot_number] = list(data.consumable_slots[slot_number])
    consumable_inventory = ConsumableInventory(consumable_slots)
    item_slots = [
        ItemInventorySlot(None, ItemEquipmentCategory.NECK),
        ItemInventorySlot(None, ItemEquipmentCategory.HEAD),
        ItemInventorySlot(None, ItemEquipmentCategory.RING),
        ItemInventorySlot(None, ItemEquipmentCategory.MAIN_HAND),
        ItemInventorySlot(None, ItemEquipmentCategory.CHEST),
        ItemInventorySlot(None, ItemEquipmentCategory.OFF_HAND),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None),
        ItemInventorySlot(None, None)
    ]
    item_inventory = ItemInventory(item_slots)
    health_resource = HealthOrManaResource(data.health, 0)
    mana_resource = HealthOrManaResource(data.mana, data.mana_regen)
    return PlayerState(
        health_resource, mana_resource, consumable_inventory, list(data.abilities), item_inventory,
        data.new_level_abilities, data.hero_id, data.armor, data.dodge_chance, data.level_bonus, data.talents_state,
        data.block_chance, 0.05, enabled_portals)


def create_warp_point(center_pos: Tuple[int, int], size: Tuple[int, int]) -> WarpPoint:
    entity = WorldEntity(get_position_from_center_position(center_pos, size), size, Sprite.WARP_POINT)
    entity.visible = False  # Warp points start out invisible and are later made visible
    return WarpPoint(entity)
