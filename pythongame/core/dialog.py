from typing import Tuple, List, Optional

from pythongame.core.common import is_x_and_y_within_distance
from pythongame.core.game_state import NonPlayerCharacter, GameState
from pythongame.core.npc_behaviors import invoke_npc_action
from pythongame.core.view import NpcActionText, DialogGraphics
from pythongame.core.view_state import ViewState


class DialogState:
    def __init__(self, view_state: ViewState):
        self.view_state = view_state
        self.npc_active_in_dialog: NonPlayerCharacter = None
        self.npc_ready_for_dialog: NonPlayerCharacter = None

    def check_if_npcs_are_close_enough_for_dialog(self, player_position: Tuple[int, int],
                                                  npcs_with_dialog: List[NonPlayerCharacter]):
        self.npc_ready_for_dialog = None
        for npc_with_dialog in npcs_with_dialog:
            close_to_player = is_x_and_y_within_distance(
                player_position, npc_with_dialog.world_entity.get_position(), 75)
            if close_to_player and not self.npc_active_in_dialog:
                self.npc_ready_for_dialog = npc_with_dialog

    def handle_user_clicked_space(self, game_state: GameState):
        if self.npc_ready_for_dialog:
            self.npc_active_in_dialog = self.npc_ready_for_dialog
            self.npc_ready_for_dialog = None
        elif self.npc_active_in_dialog:
            message = invoke_npc_action(self.npc_active_in_dialog.npc_type, game_state)
            if message:
                self.view_state.set_message(message)
            self.npc_active_in_dialog = False

    def handle_player_moved(self):
        if self.npc_active_in_dialog:
            self.npc_active_in_dialog = None

    def get_action_text(self) -> Optional[NpcActionText]:
        if self.npc_ready_for_dialog:
            return NpcActionText(self.npc_ready_for_dialog, "[Space] Talk")

    def get_dialog(self) -> Optional[DialogGraphics]:
        if self.npc_active_in_dialog:
            return DialogGraphics(self.npc_active_in_dialog.portrait_icon_sprite, self.npc_active_in_dialog.dialog)
