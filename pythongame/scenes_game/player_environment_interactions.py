import sys
from typing import Optional, Any, List

from pythongame.core.game_data import CONSUMABLES, PORTALS, get_item_data_by_type
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    ConsumableOnGround, ItemOnGround, Chest, Shrine
from pythongame.core.game_state import WorldEntity
from pythongame.core.item_effects import create_item_description
from pythongame.core.math import boxes_intersect, is_x_and_y_within_distance, \
    get_manhattan_distance_between_rects
from pythongame.core.npc_behaviors import has_npc_dialog
from pythongame.core.view.game_world_view import EntityActionText
from pythongame.scenes_game.game_engine import GameEngine


class PlayerInteractionsState:
    def __init__(self):
        self.entity_to_interact_with: Any = None

    def handle_nearby_entities(self, player_entity: WorldEntity, game_state: GameState, game_engine: GameEngine):
        self.entity_to_interact_with = None
        player_position = player_entity.get_position()
        distance_to_closest_entity = sys.maxsize

        for npc in game_state.non_player_characters:
            if has_npc_dialog(npc.npc_type):
                close_to_player = is_x_and_y_within_distance(player_position, npc.world_entity.get_position(), 75)
                distance = get_manhattan_distance_between_rects(player_entity.rect(), npc.world_entity.rect())
                if close_to_player and distance < distance_to_closest_entity:
                    self.entity_to_interact_with = npc
                    distance_to_closest_entity = distance

        lootables_on_ground: List[LootableOnGround] = list(game_state.items_on_ground)
        lootables_on_ground += game_state.consumables_on_ground
        for lootable in lootables_on_ground:
            if boxes_intersect(player_entity.rect(), lootable.world_entity.rect()):
                self.entity_to_interact_with = lootable
                distance_to_closest_entity = 0

        for portal in game_state.portals:
            close_to_player = is_x_and_y_within_distance(player_position, portal.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), portal.world_entity.rect())
            if close_to_player:
                game_engine.handle_being_close_to_portal(portal)
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = portal
                distance_to_closest_entity = distance

        for warp_point in game_state.warp_points:
            close_to_player = is_x_and_y_within_distance(player_position, warp_point.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), warp_point.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = warp_point
                distance_to_closest_entity = distance

        for chest in game_state.chests:
            close_to_player = is_x_and_y_within_distance(player_position, chest.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), chest.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = chest
                distance_to_closest_entity = distance

        for shrine in game_state.shrines:
            close_to_player = is_x_and_y_within_distance(player_position, shrine.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), shrine.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = shrine
                distance_to_closest_entity = distance

    def get_entity_to_interact_with(self):
        return self.entity_to_interact_with

    def get_entity_action_text(self, is_shift_key_held_down: bool) -> Optional[EntityActionText]:
        if self.entity_to_interact_with is None:
            return None
        return _get_entity_action_text(self.entity_to_interact_with, is_shift_key_held_down)


def _get_entity_action_text(ready_entity: Any, is_shift_key_held_down: bool) -> Optional[EntityActionText]:
    if isinstance(ready_entity, NonPlayerCharacter):
        return EntityActionText(ready_entity.world_entity, "[Space] ...", [])
    elif isinstance(ready_entity, LootableOnGround):
        loot_name = _get_loot_name(ready_entity)
        if is_shift_key_held_down:
            loot_details = _get_loot_details(ready_entity)
        else:
            loot_details = []
        return EntityActionText(ready_entity.world_entity, "[Space] " + loot_name, loot_details)
    elif isinstance(ready_entity, Portal):
        if ready_entity.is_enabled:
            data = PORTALS[ready_entity.portal_id]
            return EntityActionText(ready_entity.world_entity, "[Space] " + data.destination_name, [])
        else:
            return EntityActionText(ready_entity.world_entity, "[Space] ???", [])
    elif isinstance(ready_entity, WarpPoint):
        return EntityActionText(ready_entity.world_entity, "[Space] Warp", [])
    elif isinstance(ready_entity, Chest):
        return EntityActionText(ready_entity.world_entity, "[Space] Open", [])
    elif isinstance(ready_entity, Shrine):
        if ready_entity.has_been_used:
            return None
        else:
            return EntityActionText(ready_entity.world_entity, "[Space] Touch", [])
    else:
        raise Exception("Unhandled entity: " + str(ready_entity))


def _get_loot_name(lootable: LootableOnGround) -> str:
    if isinstance(lootable, ConsumableOnGround):
        return CONSUMABLES[lootable.consumable_type].name
    if isinstance(lootable, ItemOnGround):
        item_type = lootable.item_id.item_type
        return get_item_data_by_type(item_type).name


def _get_loot_details(lootable: LootableOnGround) -> List[str]:
    if isinstance(lootable, ConsumableOnGround):
        return [CONSUMABLES[lootable.consumable_type].description]
    if isinstance(lootable, ItemOnGround):
        return create_item_description(lootable.item_id)
