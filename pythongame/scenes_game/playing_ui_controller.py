from typing import Optional, Tuple, List

from pythongame.core.game_state import NonPlayerCharacter
from pythongame.core.npc_behaviors import get_dialog_data
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, EventTriggeredFromUi


# TODO
# Fix state handling of view code
# Currently there are:

# PlayingUiController
#   item/consumable being dragged
# GameUiState
#   map, toggles state, time info (highlight), message
# GameUiView
#   player data like abilities, consumables, items, stats, talents


# To fix:
#


class PlayingUiController:

    def __init__(self, ui_view: GameUiView, ui_state: GameUiState):
        self.ui_view = ui_view
        self.ui_state = ui_state

    def render(self):
        self.ui_view.render(
            ui_state=self.ui_state,
            is_paused=False,
        )

    def handle_mouse_movement(self, mouse_screen_position: Tuple[int, int]):
        self.ui_view.handle_mouse_movement(mouse_screen_position)

    def handle_mouse_right_click(self):
        return self.ui_view.handle_mouse_right_click()

    def handle_mouse_click(self) -> List[EventTriggeredFromUi]:
        event = self.ui_view.handle_mouse_click()
        return [event] if event else []

    def handle_mouse_release(self) -> List[EventTriggeredFromUi]:
        return self.ui_view.handle_mouse_release()

    def change_dialog_option(self, delta: int):
        self.ui_view.change_dialog_option(delta)

    def start_dialog_with_npc(self, npc: NonPlayerCharacter):
        self.ui_view.start_dialog_with_npc(npc, get_dialog_data(npc.npc_type))

    def has_open_dialog(self) -> bool:
        return self.ui_view.has_open_dialog()

    def handle_space_click(self) -> Optional[Tuple[NonPlayerCharacter, int]]:
        return self.ui_view.handle_space_click()
