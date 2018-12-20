from typing import Tuple

from pythongame.core.common import EnemyType, Direction
from pythongame.core.enemy_behaviors import create_enemy_mind
from pythongame.core.game_data import ENEMIES
from pythongame.core.game_state import WorldEntity, Enemy
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder

# TODO handle this (global path finder) in a better way!

global_path_finder: GlobalPathFinder = None


def set_global_path_finder(_global_path_finder: GlobalPathFinder):
    global global_path_finder
    global_path_finder = _global_path_finder


def create_enemy(enemy_type: EnemyType, pos: Tuple[int, int]) -> Enemy:
    data = ENEMIES[enemy_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    enemy_mind = create_enemy_mind(enemy_type, global_path_finder)
    return Enemy(enemy_type, entity, data.max_health, data.max_health, data.health_regen, enemy_mind)
