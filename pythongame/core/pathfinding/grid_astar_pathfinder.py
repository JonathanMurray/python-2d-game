from typing import Tuple, Dict, List, Any, Optional

from pythongame.core.pathfinding.astar import AStar


class GridBasedAStar(AStar):

    def __init__(self, grid, agent_size: Tuple[int, int]):
        # Grid is a 2d vector with 1s or 0s.
        # 1 == cell is blocked
        # 0 == cell is free
        # We can create the grid based on wall positions
        # Wall size is (50, 50) and all walls are placed on the (50, 50) grid
        self.grid = grid
        self.agent_size = agent_size
        self._cache_is_cell_free: Dict[Tuple[int, int], bool] = {}

        # Need to be initialized before running pathfinder
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

    def set_pathfinding_bounds(self, min_x, min_y, max_x, max_y):
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def heuristic_cost_estimate(self, current, goal):
        return abs(current[0] - goal[0]) + abs(current[1] - goal[1])

    def distance_between(self, n1, n2):
        return 1

    def neighbors(self, node):
        x, y = node
        adjacent_cells = [
            (x, y - 1),  # up
            (x - 1, y),  # left
            (x + 1, y),  # right
            (x, y + 1),  # down
        ]
        return [cell for cell in adjacent_cells if self._is_cell_free(cell[0], cell[1])]

    def _is_cell_free(self, x, y):
        # Ignore cells that are too far out, to save resources. If agent strays too far, the path is aborted.
        if not (self.min_x <= x <= self.max_x and self.min_y <= y <= self.max_y):
            return False

        if (x, y) in self._cache_is_cell_free:
            return self._cache_is_cell_free[(x, y)]
        else:
            is_free = self._compute_is_cell_free(x, y)
            self._cache_is_cell_free[(x, y)] = is_free
            return is_free

    def _compute_is_cell_free(self, x, y):
        # Check that all relevant cells are within the map
        if x < 0 or y < 0 or x + self.agent_size[0] >= len(self.grid) or y + self.agent_size[1] >= len(self.grid[x]):
            return False
        for _x in range(x, x + self.agent_size[0]):
            for _y in range(y, y + self.agent_size[1]):
                # Check if there is a wall at cell: if so, it's not free
                if self.grid[_x][_y] == 1:
                    return False
        return True


# One instance of this class is shared by all enemies. This should allow for better caching of computations
class GlobalPathFinder:
    def __init__(self):
        self.grid = None  # grid must be set before you can use the pathfinder
        self.astars_by_entity_size: Dict[Tuple[int, int], GridBasedAStar] = {}

    def set_grid(self, grid):
        self.grid = grid

    def register_entity_size(self, size: Tuple[int, int]):
        if not size in self.astars_by_entity_size:
            self.astars_by_entity_size[size] = GridBasedAStar(self.grid, size)

    def run(self, entity_size: Tuple[int, int], start_cell: Tuple[int, int], goal_cell: Tuple[int, int]) \
            -> Optional[List[Any]]:

        astar = self.astars_by_entity_size[entity_size]
        path_max_distance_from_start = 20
        astar.set_pathfinding_bounds(start_cell[0] - path_max_distance_from_start,
                                     start_cell[1] - path_max_distance_from_start,
                                     start_cell[0] + path_max_distance_from_start,
                                     start_cell[1] + path_max_distance_from_start)
        result = astar.astar(start_cell, goal_cell)

        # TODO: Handle this in a better way
        # HACK:
        if result is None:
            # print("Couldn't find path. Trying with position right above player instead.")
            goal_cell_2 = (goal_cell[0], goal_cell[1] - 1)
            result = astar.astar(start_cell, goal_cell_2)
            if result is None:
                goal_cell_3 = (goal_cell[0] - 1, goal_cell[1])
                result = astar.astar(start_cell, goal_cell_3)

        if result is None:
            return None

        path_list = []
        for x in result:
            path_list.append(x)

        return path_list
