import sys
from typing import Optional, List

from pythongame.core.common import SoundId
from pythongame.core.game_data import CONSUMABLES, ITEMS
from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, LootableOnGround, Portal, \
    ConsumableOnGround, ItemOnGround, WarpPoint
from pythongame.core.math import boxes_intersect, is_x_and_y_within_distance, \
    get_manhattan_distance_between_rects, get_directions_to_position
from pythongame.core.npc_behaviors import invoke_npc_action, has_npc_dialog, get_dialog_graphics, get_dialog_data
from pythongame.core.sound_player import play_sound
from pythongame.core.view import EntityActionText, DialogGraphics
from pythongame.core.view_state import ViewState


class PlayerInteractionsState:
    def __init__(self, view_state: ViewState):
        self.view_state = view_state
        self.npc_active_in_dialog: NonPlayerCharacter = None
        self.npc_ready_for_dialog: NonPlayerCharacter = None
        self.lootable_ready_to_be_picked_up: LootableOnGround = None
        self.portal_ready_for_interaction: Portal = None
        self.warp_point_ready_for_interaction: WarpPoint = None
        self.active_dialog_option_index = 0
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
                if close_to_player and distance < closest_distance_to_player and not self.npc_active_in_dialog:
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

    def handle_user_clicked_space(self, game_state: GameState, game_engine: GameEngine):
        if self.npc_ready_for_dialog:
            self.npc_active_in_dialog = self.npc_ready_for_dialog
            self.npc_active_in_dialog.world_entity.direction = get_directions_to_position(
                self.npc_active_in_dialog.world_entity, game_state.player_entity.get_center_position())[0]
            self.npc_active_in_dialog.world_entity.set_not_moving()
            self.npc_active_in_dialog.stun_status.add_one()
            num_dialog_options = len(get_dialog_data(self.npc_active_in_dialog.npc_type).options)
            if self.active_dialog_option_index >= num_dialog_options:
                # If you talk to one NPC, and leave with option 2, then start talking to an NPC that has just one option
                # we'd get an IndexError if we don't clear the index here. Still, it's useful to keep the index in the
                # case that you want to talk to the same NPC rapidly over and over (to buy potions for example)
                self.active_dialog_option_index = 0
            self.npc_ready_for_dialog = None
            play_sound(SoundId.DIALOG)
        elif self.npc_active_in_dialog:
            message = invoke_npc_action(self.npc_active_in_dialog.npc_type, self.active_dialog_option_index, game_state)
            if message:
                self.view_state.set_message(message)
            self.npc_active_in_dialog.stun_status.remove_one()
            self.npc_active_in_dialog = None
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

    def get_dialog(self) -> Optional[DialogGraphics]:
        if self.npc_active_in_dialog:
            return get_dialog_graphics(self.npc_active_in_dialog.npc_type, self.active_dialog_option_index)

    def is_player_in_dialog(self) -> bool:
        return self.npc_active_in_dialog is not None

    def change_dialog_option(self, option_index_delta: int):
        num_options = len(get_dialog_data(self.npc_active_in_dialog.npc_type).options)
        self.active_dialog_option_index = (self.active_dialog_option_index + option_index_delta) % num_options
        play_sound(SoundId.DIALOG)


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
