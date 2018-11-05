from pythongame.common import *


def create_enemy_mind(enemy_behavior: EnemyBehavior):
    return enemy_mind_constructors[enemy_behavior]()


enemy_mind_constructors = {}


def register_enemy_behavior(enemy_behavior: EnemyBehavior, mind_constructor):
    enemy_mind_constructors[enemy_behavior] = mind_constructor
