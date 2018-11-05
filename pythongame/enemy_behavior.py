from typing import Any, Dict

from pythongame.common import *


def create_enemy_mind(enemy_behavior: EnemyBehavior):
    return enemy_mind_constructors[enemy_behavior]()


enemy_mind_constructors: Dict[EnemyBehavior, Any] = {}


# TODO: Create an interface for the EnemyMind classes


def register_enemy_behavior(enemy_behavior: EnemyBehavior, mind_constructor):
    enemy_mind_constructors[enemy_behavior] = mind_constructor
