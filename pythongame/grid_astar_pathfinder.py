from pythongame.astar import AStar


class GridBasedAStar(AStar):

    def __init__(self, grid):
        # Grid is a 2d vector with 1s or 0s.
        # 1 == cell is blocked
        # 0 == cell is free
        # We can create the grid based on wall positions
        # Wall size is (50, 50) and all walls are placed on the (50, 50) grid
        self.grid = grid


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
        return [cell for cell in adjacent_cells if self.is_cell_free(cell)]

    def is_cell_free(self, cell):
        x, y = cell
        if 0 <= x < len(self.grid):
            if 0 <= y < len(self.grid[x]):
                return self.grid[x][y] == 0
        return False


def run_pathfinder(grid, start_cell, goal_cell):
    result = GridBasedAStar(grid).astar(start_cell, goal_cell)
    path_list = []
    if result is None:
        return None
    else:
        for x in result:
            path_list.append(x)
    return path_list