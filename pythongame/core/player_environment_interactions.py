from typing import Optional, List

from pythongame.core.common import is_x_and_y_within_distance, boxes_intersect
from pythongame.core.game_engine import GameEngine
from pythongame.core.game_state import NonPlayerCharacter, GameState, WorldEntity, LootableOnGround
from pythongame.core.npc_behaviors import invoke_npc_action
from pythongame.core.view import EntityActionText, DialogGraphics
from pythongame.core.view_state import ViewState


class PlayerInteractionsState:
    def __init__(self, view_state: ViewState):
        self.view_state = view_state
        self.npc_active_in_dialog: NonPlayerCharacter = None
        self.npc_ready_for_dialog: NonPlayerCharacter = None
        self.lootable_ready_to_be_picked_up: LootableOnGround = None

    def handle_interactions(self, player_entity: WorldEntity, game_state: GameState):
        player_position = player_entity.get_position()
        self.npc_ready_for_dialog = None
        self.lootable_ready_to_be_picked_up = None
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

    def handle_player_moved(self):
        if self.npc_active_in_dialog:
            self.npc_active_in_dialog = None

    def get_action_text(self) -> Optional[EntityActionText]:
        if self.npc_ready_for_dialog:
            return EntityActionText(self.npc_ready_for_dialog.world_entity, "[Space] Talk")
        elif self.lootable_ready_to_be_picked_up:
            return EntityActionText(self.lootable_ready_to_be_picked_up.world_entity, "[Space] Loot")

    def get_dialog(self) -> Optional[DialogGraphics]:
        if self.npc_active_in_dialog:
            return DialogGraphics(self.npc_active_in_dialog.portrait_icon_sprite, self.npc_active_in_dialog.dialog)
