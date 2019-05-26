from typing import Tuple

from pythongame.core.common import NpcType, Direction
from pythongame.core.game_data import NON_PLAYER_CHARACTERS
from pythongame.core.game_state import WorldEntity, NonPlayerCharacter
from pythongame.core.npc_behaviors import create_npc_mind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder

# TODO handle this (global path finder) in a better way!

global_path_finder: GlobalPathFinder = None


def set_global_path_finder(_global_path_finder: GlobalPathFinder):
    global global_path_finder
    global_path_finder = _global_path_finder


def create_npc(npc_type: NpcType, pos: Tuple[int, int]) -> NonPlayerCharacter:
    data = NON_PLAYER_CHARACTERS[npc_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    npc_mind = create_npc_mind(npc_type, global_path_finder)
    return NonPlayerCharacter(npc_type, entity, data.max_health, data.max_health, data.health_regen, npc_mind,
                              data.is_enemy, data.is_neutral)
