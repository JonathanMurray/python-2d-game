from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


class AbstractEnemyMind:

    def __init__(self, _global_path_finder: GlobalPathFinder):
        pass

    def control_enemy(self,
                      game_state: GameState,
                      npc: NonPlayerCharacter,
                      player_entity: WorldEntity,
                      is_player_invisible: bool,
                      time_passed: Millis):
        pass


_enemy_mind_constructors: Dict[NpcType, Type[AbstractEnemyMind]] = {}


def register_enemy_behavior(npc_type: NpcType, mind_constructor: Type[AbstractEnemyMind]):
    _enemy_mind_constructors[npc_type] = mind_constructor


def create_enemy_mind(npc_type: NpcType, global_path_finder: GlobalPathFinder):
    constructor = _enemy_mind_constructors[npc_type]
    return constructor(global_path_finder)
