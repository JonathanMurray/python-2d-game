import sys
from typing import Optional, List

from pythongame.core.game_data import CONSUMABLES, ITEMS
from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, LootableOnGround, Portal, \
    ConsumableOnGround, ItemOnGround, WarpPoint
from pythongame.core.math import boxes_intersect, is_x_and_y_within_distance, \
    get_manhattan_distance_between_rects
from pythongame.core.npc_behaviors import has_npc_dialog
from pythongame.core.view import EntityActionText


class PlayerInteractionsState:
    def __init__(self):
        self.npc_ready_for_dialog: NonPlayerCharacter = None
        self.lootable_ready_to_be_picked_up: LootableOnGround = None
        self.portal_ready_for_interaction: Portal = None
        self.warp_point_ready_for_interaction: WarpPoint = None
        self.is_shift_key_held_down = False

    def handle_interactions(self, player_entity: WorldEntity, game_state: GameState, game_engine: GameEngine):
        player_position = player_entity.get_position()
        self.npc_ready_for_dialog = None
        self.lootable_ready_to_be_picked_up = None
        self.portal_ready_for_interaction = None
        self.warp_point_ready_for_interaction = None
        closest_distance_to_player = sys.maxsize
        for npc in game_state.non_player_characters:
            if has_npc_dialog(npc.npc_type):
                close_to_player = is_x_and_y_within_distance(player_position, npc.world_entity.get_position(), 75)
                distance = get_manhattan_distance_between_rects(player_entity.rect(), npc.world_entity.rect())
                if close_to_player and distance < closest_distance_to_player:
                    self.npc_ready_for_dialog = npc
                    closest_distance_to_player = distance
        lootables_on_ground: List[LootableOnGround] = \
            game_state.items_on_ground + game_state.consumables_on_ground
        for lootable in lootables_on_ground:
            if boxes_intersect(player_entity.rect(), lootable.world_entity.rect()):
                self.npc_ready_for_dialog = None
                self.lootable_ready_to_be_picked_up = lootable
                closest_distance_to_player = 0
        for portal in game_state.portals:
            close_to_player = is_x_and_y_within_distance(player_position, portal.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), portal.world_entity.rect())

            if close_to_player:
                game_engine.handle_being_close_to_portal(portal)
            if close_to_player and distance < closest_distance_to_player:
                self.npc_ready_for_dialog = None
                self.lootable_ready_to_be_picked_up = None
                self.portal_ready_for_interaction = portal
                closest_distance_to_player = distance
        for warp_point in game_state.warp_points:
            close_to_player = is_x_and_y_within_distance(player_position, warp_point.world_entity.get_position(), 75)
            distance = get_manhattan_distance_between_rects(player_entity.rect(), warp_point.world_entity.rect())
            if close_to_player and distance < closest_distance_to_player:
                self.npc_ready_for_dialog = None
                self.lootable_ready_to_be_picked_up = None
                self.portal_ready_for_interaction = None
                self.warp_point_ready_for_interaction = warp_point
                closest_distance_to_player = distance

    def handle_user_clicked_space(self, game_engine: GameEngine) -> Optional[NonPlayerCharacter]:
        if self.npc_ready_for_dialog:
            npc = self.npc_ready_for_dialog
            self.npc_ready_for_dialog = None
            return npc
        elif self.lootable_ready_to_be_picked_up:
            game_engine.try_pick_up_loot_from_ground(self.lootable_ready_to_be_picked_up)
        elif self.portal_ready_for_interaction:
            game_engine.interact_with_portal(self.portal_ready_for_interaction)
        elif self.warp_point_ready_for_interaction:
            game_engine.use_warp_point(self.warp_point_ready_for_interaction)

    def handle_user_pressed_shift(self):
        self.is_shift_key_held_down = True

    def handle_user_released_shift(self):
        self.is_shift_key_held_down = False

    def get_action_text(self) -> Optional[EntityActionText]:
        if self.npc_ready_for_dialog:
            return EntityActionText(self.npc_ready_for_dialog.world_entity, "[Space] ...", None)
        elif self.lootable_ready_to_be_picked_up:
            loot_name = _get_loot_name(self.lootable_ready_to_be_picked_up)
            if self.is_shift_key_held_down:
                loot_details = "> " + _get_loot_details(self.lootable_ready_to_be_picked_up)
            else:
                loot_details = None
            return EntityActionText(self.lootable_ready_to_be_picked_up.world_entity, "[Space] " + loot_name,
                                    loot_details)
        elif self.portal_ready_for_interaction:
            if self.portal_ready_for_interaction.is_enabled:
                return EntityActionText(self.portal_ready_for_interaction.world_entity, "[Space] Warp", None)
            else:
                return EntityActionText(self.portal_ready_for_interaction.world_entity, "[Space] ???", None)
        elif self.warp_point_ready_for_interaction:
            return EntityActionText(self.warp_point_ready_for_interaction.world_entity, "[Space] Warp", None)


def _get_loot_name(lootable: LootableOnGround) -> str:
    if isinstance(lootable, ConsumableOnGround):
        return CONSUMABLES[lootable.consumable_type].name
    if isinstance(lootable, ItemOnGround):
        return ITEMS[lootable.item_type].name


def _get_loot_details(lootable: LootableOnGround) -> str:
    if isinstance(lootable, ConsumableOnGround):
        return CONSUMABLES[lootable.consumable_type].description
    if isinstance(lootable, ItemOnGround):
        return ITEMS[lootable.item_type].description
