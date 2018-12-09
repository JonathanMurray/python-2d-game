from typing import Tuple, Any, Optional

from pythongame.core.common import Millis, is_x_and_y_within_distance, get_directions_to_position, \
    get_opposite_direction, \
    Direction
from pythongame.core.game_state import GRID_CELL_WIDTH, GameState, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import VisualLine, VisualRect

DEBUG_RENDER_PATHFINDING = False
DEBUG_PATHFINDER_INTERVAL = 900


class EnemyPathfinder:

    def __init__(self, global_path_finder):
        self.path = None
        self.global_path_finder: GlobalPathFinder = global_path_finder

    def update_path(self, enemy_entity: WorldEntity, game_state):
        enemy_cell = _get_cell_from_position(enemy_entity.get_position())
        player_cell = _get_cell_from_position(game_state.player_entity.get_position())

        agent_cell_size = (enemy_entity.w // GRID_CELL_WIDTH + 1, enemy_entity.h // GRID_CELL_WIDTH + 1)
        self.global_path_finder.register_entity_size(agent_cell_size)
        path_with_cells = self.global_path_finder.run(agent_cell_size, enemy_cell, player_cell)
        if path_with_cells:
            path = [(cell[0] * GRID_CELL_WIDTH, cell[1] * GRID_CELL_WIDTH) for cell in path_with_cells]
            if DEBUG_RENDER_PATHFINDING:
                _add_visual_lines_along_path(game_state, path)
            self.path = path
        else:
            self.path = None

    def get_next_waypoint_along_path(self, enemy_entity: WorldEntity) -> Optional[Any]:
        if self.path:
            # -----------------------------------------------
            # 1: Remove first waypoint if close enough to it
            # -----------------------------------------------
            # TODO: Does this cause problems for specific entity sizes / movement speeds?
            closeness_margin = 50
            if is_x_and_y_within_distance(enemy_entity.get_position(), self.path[0], closeness_margin):
                # print("Popping " + str(self.path[0]) + " as I'm so close to it.")
                self.path.pop(0)
                if self.path:
                    # print("After popping, returning " + str(self.path[0]))
                    return self.path[0]
                else:
                    # print("no path after popping. stopping.")
                    return None

            # -----------------------------------------------
            # 2: Remove first waypoint if it's opposite direction of second waypoint
            # -----------------------------------------------
            if len(self.path) >= 2:
                dir_to_waypoint_0 = get_directions_to_position(enemy_entity, self.path[0])[0]
                dir_to_waypoint_1 = get_directions_to_position(enemy_entity, self.path[1])[0]
                if dir_to_waypoint_0 == get_opposite_direction(dir_to_waypoint_1):
                    # print("Not gonna go back. Popping " + str(self.path[0]))
                    self.path.pop(0)
                    # print("position: " + str((enemy_entity.x, enemy_entity.y)))
                    # print("Popped first position. Next waypoint: " + str(self.path[0]))
                    return self.path[0]
                if self.path:
                    return self.path[0]
        else:
            # print("no path found. stopping.")
            return None
        # print("Leaked through. returning none")
        return None

    @staticmethod
    def get_dir_towards_considering_collisions(game_state: GameState, enemy_entity: WorldEntity,
                                               destination: Tuple[int, int]) -> Optional[Direction]:
        if DEBUG_RENDER_PATHFINDING:
            _add_visual_line_to_next_waypoint(destination, enemy_entity, game_state)
        directions = get_directions_to_position(enemy_entity, destination)
        if directions:
            # TODO Refactor collision checking
            # enemy_entity.set_moving_in_dir(directions[0])
            if _would_collide_with_dir(directions[0], enemy_entity, game_state):
                if len(directions) > 1 and directions[1]:
                    # print("Colliding in main direction (" + str(directions[0]) + ")")
                    if not _would_collide_with_dir(directions[1], enemy_entity, game_state):
                        # print("Will use other direction")
                        return directions[1]
                    else:
                        # print("Both directions collide...")
                        return None
                else:
                    # print("Colliding in main direction (" + str(directions[0]) + ") but there is no other choice")
                    return None
            else:
                return directions[0]
        return None


def _add_visual_line_to_next_waypoint(destination, enemy_entity, game_state):
    game_state.visual_effects.append(
        VisualLine((150, 150, 150), _get_middle_of_cell_from_position(enemy_entity.get_position()),
                   _get_middle_of_cell_from_position(destination), Millis(100), 2))


def _add_visual_lines_along_path(game_state, path):
    for i in range(len(path) - 1):
        current_pos = path[i]
        next_pos = path[i + 1]
        game_state.visual_effects.append(
            VisualRect((100, 150, 150),
                       _get_middle_of_cell_from_position(current_pos), 7, 10, Millis(DEBUG_PATHFINDER_INTERVAL), 1))
        game_state.visual_effects.append(
            VisualLine((250, 250, 250),
                       _get_middle_of_cell_from_position(current_pos),
                       _get_middle_of_cell_from_position(next_pos),
                       Millis(DEBUG_PATHFINDER_INTERVAL), 1))


def _get_middle_of_cell_from_position(position):
    return position[0] + GRID_CELL_WIDTH // 2, position[1] + GRID_CELL_WIDTH // 2


def _would_collide_with_dir(direction: Direction, enemy_entity: WorldEntity, game_state: GameState):
    # TODO Is this too naive to work?
    future_time = Millis(100)
    future_pos = enemy_entity.get_new_position_according_to_other_dir_and_speed(direction, future_time)
    future_pos_within_world = game_state.get_within_world(future_pos, (enemy_entity.w, enemy_entity.h))
    would_collide = game_state.would_entity_collide_if_new_pos(enemy_entity, future_pos_within_world)
    return would_collide


def _get_cell_from_position(position):
    return (int((position[0] + GRID_CELL_WIDTH / 2) // GRID_CELL_WIDTH),
            int((position[1] + GRID_CELL_WIDTH / 2) // GRID_CELL_WIDTH))
