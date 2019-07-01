from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


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

    def act(self, game_state: GameState):
        pass


_npc_mind_constructors: Dict[NpcType, Type[AbstractNpcMind]] = {}

_npc_actions: Dict[NpcType, AbstractNpcAction] = {}


def register_npc_behavior(npc_type: NpcType, mind_constructor: Type[AbstractNpcMind]):
    _npc_mind_constructors[npc_type] = mind_constructor


def create_npc_mind(npc_type: NpcType, global_path_finder: GlobalPathFinder):
    constructor = _npc_mind_constructors[npc_type]
    return constructor(global_path_finder)


def register_npc_action(npc_type: NpcType, action: AbstractNpcAction):
    _npc_actions[npc_type] = action


def invoke_npc_action(npc_type: NpcType, game_state: GameState):
    _npc_actions[npc_type].act(game_state)
