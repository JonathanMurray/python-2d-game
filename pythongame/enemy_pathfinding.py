from typing import Tuple

from pythongame.common import Millis, is_x_and_y_within_distance, get_directions_to_position, get_opposite_direction
from pythongame.game_state import GRID_CELL_WIDTH, GameState, WorldEntity, Enemy
from pythongame.grid_astar_pathfinder import run_pathfinder
from pythongame.visual_effects import VisualLine

DEBUG_RENDER_PATHFINDING = False
DEBUG_PATHFINDER_INTERVAL = 900


class EnemyPathfinder:

    def __init__(self):
        self.path = None

    def update_path(self, enemy, game_state):
        enemy_position = enemy.world_entity.get_center_position()
        enemy_cell = (enemy_position[0] // GRID_CELL_WIDTH, enemy_position[1] // GRID_CELL_WIDTH)
        player_position = game_state.player_entity.get_center_position()
        player_cell = (player_position[0] // GRID_CELL_WIDTH, player_position[1] // GRID_CELL_WIDTH)
        print("From " + str(enemy_position) + " to " + str(player_position))
        print("Cell " + str(enemy_cell) + " to " + str(player_cell))
        path_with_cells = run_pathfinder(game_state.grid, enemy_cell, player_cell)
        if path_with_cells:
            path = [(cell[0] * GRID_CELL_WIDTH, cell[1] * GRID_CELL_WIDTH) for cell in path_with_cells]
            print("Found new path: " + str(path))
            print("Position: " + str((enemy.world_entity.x, enemy.world_entity.y)))
            if DEBUG_RENDER_PATHFINDING:
                for i in range(len(path) - 1):
                    game_state.visual_effects.append(
                        VisualLine((250, 250, 250), path[i],
                                   path[i + 1], Millis(DEBUG_PATHFINDER_INTERVAL), 3))
            self.path = path
        else:
            self.path = None

    def move_enemy_along_path(self, enemy: Enemy, game_state: GameState, just_found_path: bool):
        if self.path:
            # TODO: Does this cause problems for specific entity sizes / movement speeds?
            closeness_margin = 15
            if is_x_and_y_within_distance((enemy.world_entity.x, enemy.world_entity.y), self.path[0], closeness_margin):
                self.path.pop(0)
                if self.path:
                    self._move_enemy_towards(game_state, enemy.world_entity, self.path[0])
                else:
                    enemy.world_entity.set_not_moving()
            if len(self.path) >= 2:
                dir_to_waypoint_0 = get_directions_to_position(enemy.world_entity, self.path[0])[0]
                dir_to_waypoint_1 = get_directions_to_position(enemy.world_entity, self.path[1])[0]
                if dir_to_waypoint_0 == get_opposite_direction(dir_to_waypoint_1):
                    print("Not gonna go back. Popping " + str(self.path[0]))
                    self.path.pop(0)
                    print("position: " + str((enemy.world_entity.x, enemy.world_entity.y)))
                    print("Popped first position. Next waypoint: " + str(self.path[0]))
                    if self.path:
                        self._move_enemy_towards(game_state, enemy.world_entity, self.path[0])
                    else:
                        enemy.world_entity.set_not_moving()
                        return
            if just_found_path:
                if self.path:
                    self._move_enemy_towards(game_state, enemy.world_entity, self.path[0])
        else:
            print("no path found. stopping.")
            enemy.world_entity.set_not_moving()

    def _move_enemy_towards(self, game_state: GameState, enemy_entity: WorldEntity, destination: Tuple[int, int]):
        if DEBUG_RENDER_PATHFINDING:
            game_state.visual_effects.append(
                VisualLine((0, 0, 150), (enemy_entity.x, enemy_entity.y),
                           destination, Millis(200), 2))
        directions = get_directions_to_position(enemy_entity, destination)
        if directions:
            # TODO Refactor collision checking
            enemy_entity.set_moving_in_dir(directions[0])
            future_pos = enemy_entity.get_new_position_according_to_dir_and_speed(Millis(100))
            future_pos_within_world = game_state.get_within_world(future_pos, (enemy_entity.w, enemy_entity.h))
            would_collide = game_state.would_entity_collide_if_new_pos(enemy_entity, future_pos_within_world)
            if would_collide:
                if len(directions) > 1 and directions[1]:
                    print("Colliding in main direction (" + str(directions[0]) + ") so will use " + str(directions[1]))
                    enemy_entity.set_moving_in_dir(directions[1])
                else:
                    print("Colliding in main direction (" + str(directions[0]) + ") but there is no other choice")
