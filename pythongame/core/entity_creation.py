from typing import Tuple

from pythongame.core.common import NpcType, Direction, Sprite, ItemType, ConsumableType
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, ITEM_ENTITY_SIZE, ITEMS, CONSUMABLES, POTION_ENTITY_SIZE
from pythongame.core.game_state import WorldEntity, NonPlayerCharacter, MoneyPileOnGround, ItemOnGround, \
    ConsumableOnGround, Portal
from pythongame.core.npc_behaviors import create_npc_mind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.portals import PORTAL_SIZE

# TODO handle this (global path finder) in a better way!

global_path_finder: GlobalPathFinder = None


def set_global_path_finder(_global_path_finder: GlobalPathFinder):
    global global_path_finder
    global_path_finder = _global_path_finder


def create_npc(npc_type: NpcType, pos: Tuple[int, int]) -> NonPlayerCharacter:
    data = NON_PLAYER_CHARACTERS[npc_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    npc_mind = create_npc_mind(npc_type, global_path_finder)
    return NonPlayerCharacter(npc_type, entity, data.max_health, data.max_health, data.health_regen, npc_mind,
                              data.is_enemy, data.is_neutral, data.dialog, data.portrait_icon_sprite,
                              data.enemy_loot_table)


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
    return ItemOnGround(entity, item_type)


def create_consumable_on_ground(consumable_type: ConsumableType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, CONSUMABLES[consumable_type].entity_sprite)
    return ConsumableOnGround(entity, consumable_type)


def create_portal_at_position(is_main_portal: bool, pos: Tuple[int, int]):
    sprite = Sprite.PORTAL
    if is_main_portal:
        return Portal(WorldEntity(pos, PORTAL_SIZE, sprite), 0, True, False, 1)
    else:
        return Portal(WorldEntity(pos, PORTAL_SIZE, sprite), 1, False, True, 0)
