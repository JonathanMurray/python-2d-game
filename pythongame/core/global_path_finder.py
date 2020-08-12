# NPC's share a "global path finder" that needs to be initialized before we start creating NPCs.
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder

path_finder = None


def init_global_path_finder():
    global path_finder
    path_finder = GlobalPathFinder()
    return path_finder


def get_global_path_finder():
    return path_finder
