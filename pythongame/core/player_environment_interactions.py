import sys
from typing import List, Any

from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import GameState, WorldEntity, LootableOnGround
from pythongame.core.math import boxes_intersect, is_x_and_y_within_distance, \
    get_manhattan_distance_between_rects
from pythongame.core.npc_behaviors import has_npc_dialog


class PlayerInteractionsState:
    def __init__(self):
        self.entity_to_interact_with: Any = None

    def handle_nearby_entities(self, player_entity: WorldEntity, game_state: GameState, game_engine: GameEngine):
        player_position = player_entity.get_position()
        distance_to_closest_entity = sys.maxsize

        for npc in game_state.non_player_characters:
            if has_npc_dialog(npc.npc_type):
                close_to_player = is_x_and_y_within_distance(player_position, npc.world_entity.get_position(), 75)
                distance = get_manhattan_distance_between_rects(player_entity.rect(), npc.world_entity.rect())
                if close_to_player and distance < distance_to_closest_entity:
                    self.entity_to_interact_with = npc
                    distance_to_closest_entity = distance

        lootables_on_ground: List[LootableOnGround] = \
            game_state.items_on_ground + game_state.consumables_on_ground
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

    def get_entity_to_interact_with(self):
        return self.entity_to_interact_with
