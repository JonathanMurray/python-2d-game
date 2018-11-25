from typing import Tuple, Dict

from pythongame.core.astar import AStar


class GridBasedAStar(AStar):

    def __init__(self, grid, agent_size: Tuple[int, int]):
        # Grid is a 2d vector with 1s or 0s.
        # 1 == cell is blocked
        # 0 == cell is free
        # We can create the grid based on wall positions
        # Wall size is (50, 50) and all walls are placed on the (50, 50) grid
        self.grid = grid
        self.agent_size = agent_size
        self._cache: Dict[Tuple[int, int], bool] = {}

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
        return [cell for cell in adjacent_cells if self._is_cell_free_considering_entity_size(cell[0], cell[1])]

    def _is_cell_free_considering_entity_size(self, x, y):
        if (x, y) in self._cache:
            return self._cache[(x, y)]
        else:
            is_free = self._compute_is_cell_free_considering_entity_size(x, y)
            self._cache[(x, y)] = is_free
            return is_free

    def _compute_is_cell_free_considering_entity_size(self, x, y):
        # Check that all relevant cells are within the map
        if x < 0 or y < 0 or x + self.agent_size[0] >= len(self.grid) or y + self.agent_size[1] >= len(self.grid[x]):
            return False
        for _x in range(x, x + self.agent_size[0] + 1):
            for _y in range(y, y + self.agent_size[1] + 1):
                # Check if there is a wall at cell: if so, it's not free
                if self.grid[x][y] == 1:
                    return False
        return True


def run_pathfinder(grid_based_a_star: GridBasedAStar, start_cell: Tuple[int, int], goal_cell: Tuple[int, int]):
    result = grid_based_a_star.astar(start_cell, goal_cell)

    if result is None:
        # TODO: Handle this in a better way
        # HACK:
        # print("Couldn't find path. Trying with position right above player instead.")
        goal_cell_2 = (goal_cell[0], goal_cell[1] - 1)
        result = grid_based_a_star.astar(start_cell, goal_cell_2)

    if result is None:
        return None

    path_list = []
    for x in result:
        path_list.append(x)
    return path_list
