from typing import Any, Dict

from pythongame.common import *

# TODO: Create an interface for the EnemyMind classes

_enemy_mind_constructors: Dict[EnemyBehavior, Any] = {}


def register_enemy_behavior(enemy_behavior: EnemyBehavior, mind_constructor):
    _enemy_mind_constructors[enemy_behavior] = mind_constructor


def create_enemy_mind(enemy_behavior: EnemyBehavior):
    return _enemy_mind_constructors[enemy_behavior]()
