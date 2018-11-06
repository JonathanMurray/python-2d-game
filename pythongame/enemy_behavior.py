from typing import Dict, Type

from pythongame.common import *
from pythongame.game_state import GameState, Enemy, WorldEntity


class AbstractEnemyMind:
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


def create_enemy_mind(enemy_type: EnemyType):
    return _enemy_mind_constructors[enemy_type]()
