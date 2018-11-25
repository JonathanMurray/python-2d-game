from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import GameState, Enemy, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


class AbstractEnemyMind:

    def __init__(self, _global_path_finder: GlobalPathFinder):
        pass

    def control_enemy(self,
                      game_state: GameState,
                      enemy: Enemy,
                      player_entity: WorldEntity,
                      is_player_invisible: bool,
                      time_passed: Millis):
        pass


_enemy_mind_constructors: Dict[EnemyType, Type[AbstractEnemyMind]] = {}


def register_enemy_behavior(enemy_type: EnemyType, mind_constructor: Type[AbstractEnemyMind]):
    _enemy_mind_constructors[enemy_type] = mind_constructor


def create_enemy_mind(enemy_type: EnemyType, global_path_finder: GlobalPathFinder):
    constructor = _enemy_mind_constructors[enemy_type]
    return constructor(global_path_finder)
