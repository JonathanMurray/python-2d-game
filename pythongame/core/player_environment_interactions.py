from typing import Optional, List

from pythongame.core.common import is_x_and_y_within_distance, boxes_intersect, Millis, translate_in_direction, \
    Direction
from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, LootableOnGround, Portal
from pythongame.core.npc_behaviors import invoke_npc_action
from pythongame.core.view import EntityActionText, DialogGraphics
from pythongame.core.view_state import ViewState
from pythongame.core.visual_effects import VisualCircle


class PlayerInteractionsState:
    def __init__(self, view_state: ViewState):
        self.view_state = view_state
        self.npc_active_in_dialog: NonPlayerCharacter = None
        self.npc_ready_for_dialog: NonPlayerCharacter = None
        self.lootable_ready_to_be_picked_up: LootableOnGround = None
        self.portal_ready_for_interaction: Portal = None

    def handle_interactions(self, player_entity: WorldEntity, game_state: GameState):
        player_position = player_entity.get_position()
        self.npc_ready_for_dialog = None
        self.lootable_ready_to_be_picked_up = None
        self.portal_ready_for_interaction = None
        for npc in game_state.non_player_characters:
            if npc.dialog:
                close_to_player = is_x_and_y_within_distance(player_position, npc.world_entity.get_position(), 75)
                if close_to_player and not self.npc_active_in_dialog:
                    self.npc_ready_for_dialog = npc
        lootables_on_ground: List[LootableOnGround] = \
            game_state.items_on_ground + game_state.consumables_on_ground
        for lootable in lootables_on_ground:
            if boxes_intersect(player_entity, lootable.world_entity):
                self.lootable_ready_to_be_picked_up = lootable
        for portal in game_state.portals:
            close_to_player = is_x_and_y_within_distance(player_position, portal.world_entity.get_position(), 75)
            if close_to_player:
                self.portal_ready_for_interaction = portal

    def handle_user_clicked_space(self, game_state: GameState, game_engine: GameEngine):
        if self.npc_ready_for_dialog:
            self.npc_active_in_dialog = self.npc_ready_for_dialog
            self.npc_ready_for_dialog = None
        elif self.npc_active_in_dialog:
            message = invoke_npc_action(self.npc_active_in_dialog.npc_type, game_state)
            if message:
                self.view_state.set_message(message)
            self.npc_active_in_dialog = None
        elif self.lootable_ready_to_be_picked_up:
            game_engine.try_pick_up_loot_from_ground(self.lootable_ready_to_be_picked_up)
        elif self.portal_ready_for_interaction:
            self._try_use_portal(self.portal_ready_for_interaction, game_state)

    # TODO Delegate this logic to game_engine?
    def _try_use_portal(self, portal: Portal, game_state: GameState):
        if portal.is_enabled:
            destination_portal = [p for p in game_state.portals if p.index == portal.leads_to][0]
            destination_portal.is_enabled = True
            destination = translate_in_direction(destination_portal.world_entity.get_position(), Direction.DOWN, 50)
            game_state.player_entity.set_position(destination)
            color = (140, 140, 230)
            game_state.visual_effects.append(
                VisualCircle(color, destination, 25, 50, Millis(300), 2,
                             game_state.player_entity))
        else:
            self.view_state.set_message("Hmm... Looks suspicious!")

    def handle_player_moved(self):
        if self.npc_active_in_dialog:
            self.npc_active_in_dialog = None

    def get_action_text(self) -> Optional[EntityActionText]:
        if self.npc_ready_for_dialog:
            return EntityActionText(self.npc_ready_for_dialog.world_entity, "[Space] Talk")
        elif self.lootable_ready_to_be_picked_up:
            return EntityActionText(self.lootable_ready_to_be_picked_up.world_entity, "[Space] Loot")
        elif self.portal_ready_for_interaction:
            if self.portal_ready_for_interaction.is_enabled:
                return EntityActionText(self.portal_ready_for_interaction.world_entity, "[Space] Warp")
            else:
                return EntityActionText(self.portal_ready_for_interaction.world_entity, "[Space] ???")

    def get_dialog(self) -> Optional[DialogGraphics]:
        if self.npc_active_in_dialog:
            return DialogGraphics(self.npc_active_in_dialog.portrait_icon_sprite, self.npc_active_in_dialog.dialog)
