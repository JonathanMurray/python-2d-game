import sys
from typing import Optional, Any, List, Tuple

from pythongame.core.game_data import CONSUMABLES, PORTALS
from pythongame.core.game_state import GameState, NonPlayerCharacter, LootableOnGround, Portal, WarpPoint, \
    ConsumableOnGround, ItemOnGround, Chest, Shrine, DungeonEntrance
from pythongame.core.item_data import create_item_description, get_item_data
from pythongame.core.math import boxes_intersect, is_x_and_y_within_distance, \
    get_manhattan_distance_between_rects
from pythongame.core.npc_behaviors import has_npc_dialog
from pythongame.core.view.game_world_view import EntityActionText, EntityActionTextStyle
from pythongame.core.world_entity import WorldEntity
from pythongame.scenes.scenes_game.game_engine import GameEngine


class PlayerInteractionsState:
    def __init__(self):
        self.entity_to_interact_with: Any = None

    def handle_nearby_entities(self, player_entity: WorldEntity, game_state: GameState, game_engine: GameEngine):
        self.entity_to_interact_with = None
        player_position = player_entity.get_position()
        distance_to_closest_entity = sys.maxsize

        for npc in game_state.game_world.non_player_characters:
            if has_npc_dialog(npc.npc_type):
                close_to_player = is_x_and_y_within_distance(player_position, npc.world_entity.get_position(), 75)
                distance = get_manhattan_distance_between_rects(player_entity.rect(), npc.world_entity.rect())
                if close_to_player and distance < distance_to_closest_entity:
                    self.entity_to_interact_with = npc
                    distance_to_closest_entity = distance

        lootables_on_ground: List[LootableOnGround] = list(game_state.game_world.items_on_ground)
        lootables_on_ground += game_state.game_world.consumables_on_ground
        for lootable in lootables_on_ground:
            if boxes_intersect(player_entity.rect(), lootable.world_entity.rect()):
                self.entity_to_interact_with = lootable
                distance_to_closest_entity = 0

        for portal in game_state.game_world.portals:
            close_to_player = is_x_and_y_within_distance(player_position, portal.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), portal.world_entity.rect())
            if close_to_player:
                game_engine.handle_being_close_to_portal(portal)
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = portal
                distance_to_closest_entity = distance

        for warp_point in game_state.game_world.warp_points:
            close_to_player = is_x_and_y_within_distance(player_position, warp_point.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), warp_point.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = warp_point
                distance_to_closest_entity = distance

        for chest in game_state.game_world.chests:
            close_to_player = is_x_and_y_within_distance(player_position, chest.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), chest.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = chest
                distance_to_closest_entity = distance

        for shrine in game_state.game_world.shrines:
            close_to_player = is_x_and_y_within_distance(player_position, shrine.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), shrine.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = shrine
                distance_to_closest_entity = distance

        for dungeon_entrance in game_state.game_world.dungeon_entrances:
            close_to_player = is_x_and_y_within_distance(
                player_position, dungeon_entrance.world_entity.get_position(), 60)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), dungeon_entrance.world_entity.rect())
            if close_to_player and distance < distance_to_closest_entity:
                self.entity_to_interact_with = dungeon_entrance
                distance_to_closest_entity = distance

    def get_entity_to_interact_with(self):
        return self.entity_to_interact_with

    def get_entity_action_text(self, is_shift_key_held_down: bool) -> Optional[EntityActionText]:
        if self.entity_to_interact_with is None:
            return None
        return _get_entity_action_text(self.entity_to_interact_with, is_shift_key_held_down)


def _get_entity_action_text(ready_entity: Any, is_shift_key_held_down: bool) -> Optional[EntityActionText]:
    if isinstance(ready_entity, NonPlayerCharacter):
        return EntityActionText(ready_entity.world_entity, "...", [])
    elif isinstance(ready_entity, LootableOnGround):
        name, style = _get_loot_name(ready_entity)
        if is_shift_key_held_down:
            loot_details = _get_loot_details(ready_entity)
        else:
            loot_details = []
        return EntityActionText(ready_entity.world_entity, name, loot_details, style=style)
    elif isinstance(ready_entity, Portal):
        if ready_entity.is_enabled:
            data = PORTALS[ready_entity.portal_id]
            return EntityActionText(ready_entity.world_entity, data.destination_name, [])
        else:
            return EntityActionText(ready_entity.world_entity, "???", [])
    elif isinstance(ready_entity, WarpPoint):
        return EntityActionText(ready_entity.world_entity, "Warp", [])
    elif isinstance(ready_entity, Chest):
        return EntityActionText(ready_entity.world_entity, "Open", [])
    elif isinstance(ready_entity, Shrine):
        if ready_entity.has_been_used:
            return None
        else:
            return EntityActionText(ready_entity.world_entity, "Touch", [])
    elif isinstance(ready_entity, DungeonEntrance):
        return EntityActionText(ready_entity.world_entity, "...", [])
    else:
        raise Exception("Unhandled entity: " + str(ready_entity))


def _get_loot_name(lootable: LootableOnGround) -> Tuple[str, EntityActionTextStyle]:
    if isinstance(lootable, ConsumableOnGround):
        name = CONSUMABLES[lootable.consumable_type].name
        return name, EntityActionTextStyle.PLAIN
    if isinstance(lootable, ItemOnGround):
        name = lootable.item_id.name
        if lootable.item_id.affix_stats:
            style = EntityActionTextStyle.LOOT_RARE
        elif get_item_data(lootable.item_id).is_unique:
            style = EntityActionTextStyle.LOOT_UNIQUE
        else:
            style = EntityActionTextStyle.PLAIN
        return name, style


def _get_loot_details(lootable: LootableOnGround) -> List[str]:
    if isinstance(lootable, ConsumableOnGround):
        return [CONSUMABLES[lootable.consumable_type].description]
    if isinstance(lootable, ItemOnGround):
        # TODO Render suffix lines differently?
        return [line.text for line in create_item_description(lootable.item_id)]
