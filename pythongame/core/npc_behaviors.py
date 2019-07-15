from typing import Dict, Type, Optional, List

from pythongame.core.common import *
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


# Used to display dialog from an npc along with the NPC's portrait
class DialogGraphics:
    # TODO Handle several options
    def __init__(self, portrait_icon_sprite: PortraitIconSprite, text_body: str, text_action: str):
        self.portrait_icon_sprite = portrait_icon_sprite
        self.text_body = text_body
        self.text_action = text_action


class AbstractNpcMind:

    def __init__(self, _global_path_finder: GlobalPathFinder):
        pass

    def control_npc(self,
                    game_state: GameState,
                    npc: NonPlayerCharacter,
                    player_entity: WorldEntity,
                    is_player_invisible: bool,
                    time_passed: Millis):
        pass


class AbstractNpcAction:

    # perform action, and optionally return a message to be displayed
    def act(self, game_state: GameState) -> Optional[str]:
        pass


class DialogOptionData:
    def __init__(self, text_header: str, text_detailed: str, action: Optional[AbstractNpcAction]):
        self.text_header = text_header
        self.text_detailed = text_detailed
        self.action = action


class DialogData:
    def __init__(self, portrait_icon_sprite: PortraitIconSprite, text_body: str, options: List[DialogOptionData]):
        self.portrait_icon_sprite = portrait_icon_sprite
        self.text_body = text_body
        self.options = options


_npc_mind_constructors: Dict[NpcType, Type[AbstractNpcMind]] = {}

_npc_dialog_data: Dict[NpcType, DialogData] = {}


def register_npc_behavior(npc_type: NpcType, mind_constructor: Type[AbstractNpcMind]):
    _npc_mind_constructors[npc_type] = mind_constructor


def create_npc_mind(npc_type: NpcType, global_path_finder: GlobalPathFinder):
    constructor = _npc_mind_constructors[npc_type]
    return constructor(global_path_finder)


def register_npc_dialog_data(npc_type: NpcType, data: DialogData):
    _npc_dialog_data[npc_type] = data


def invoke_npc_action(npc_type: NpcType, option_index: int, game_state: GameState) -> Optional[str]:
    action = _npc_dialog_data[npc_type].options[option_index].action
    optional_message = action.act(game_state)
    return optional_message


def has_npc_dialog(npc_type: NpcType) -> bool:
    return npc_type in _npc_dialog_data


def get_dialog_graphics(npc_type: NpcType) -> DialogGraphics:
    data = _npc_dialog_data[npc_type]
    # TODO handle several options
    return DialogGraphics(data.portrait_icon_sprite, data.text_body, data.options[0].text_detailed)
