from typing import Optional, Tuple, List

from pythongame.core.game_state import NonPlayerCharacter
from pythongame.core.npc_behaviors import get_dialog_data, DialogData
from pythongame.scenes_game.game_ui_state import GameUiState
from pythongame.scenes_game.game_ui_view import GameUiView, DialogConfig, EventTriggeredFromUi


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

class DialogState:
    def __init__(self):
        self.option_index: int = 0
        self.data: DialogData = None
        self.npc: NonPlayerCharacter = None
        self.active = False


class PlayingUiController:

    def __init__(self, ui_view: GameUiView, ui_state: GameUiState):
        self.ui_view = ui_view
        self.ui_state = ui_state
        self.dialog = DialogState()

    def render(self):

        # RENDERING
        self.ui_view.render(
            ui_state=self.ui_state,
            is_paused=False,
        )

    def handle_mouse_movement(self, mouse_screen_position: Tuple[int, int]):
        self.ui_view.handle_mouse(mouse_screen_position)

    def handle_mouse_right_click(self):
        return self.ui_view.handle_mouse_right_click()

    def handle_mouse_click(self) -> List[EventTriggeredFromUi]:
        event = self.ui_view.handle_mouse_click()
        return [event] if event else []

    def handle_mouse_release(self) -> List[EventTriggeredFromUi]:
        return self.ui_view.handle_mouse_release()

    def change_dialog_option(self, delta: int):
        self.dialog.option_index = (self.dialog.option_index + delta) % len(self.dialog.data.options)
        self.ui_view.update_dialog(DialogConfig(self.dialog.data, self.dialog.option_index))

    # TODO move this down into UiView
    def start_dialog_with_npc(self, npc: NonPlayerCharacter):
        self.dialog.active = True
        self.dialog.npc = npc
        self.dialog.data = get_dialog_data(npc.npc_type)
        if self.dialog.option_index >= len(self.dialog.data.options):
            self.dialog.option_index = 0
        self.ui_view.update_dialog(DialogConfig(self.dialog.data, self.dialog.option_index))

    def has_open_dialog(self) -> bool:
        return self.dialog.active

    # TODO move this down into UiView
    def handle_space_click(self) -> Optional[Tuple[NonPlayerCharacter, int]]:
        if self.dialog.active:
            self.dialog.active = False
            self.ui_view.update_dialog(None)
            return self.dialog.npc, self.dialog.option_index
        return None
