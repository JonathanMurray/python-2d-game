from typing import Tuple, Optional, List

from pygame.rect import Rect

from pythongame.core.common import Millis, Direction
from pythongame.core.game_state import GRID_CELL_WIDTH, GameState
from pythongame.core.math import get_directions_to_position, get_opposite_direction, is_x_and_y_within_distance
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import VisualLine, VisualRect
from pythongame.core.world_entity import WorldEntity

DEBUG_RENDER_PATHFINDING = False
DEBUG_PATHFINDER_INTERVAL = 900


class NpcPathfinder:

    def __init__(self, global_path_finder: GlobalPathFinder):
        self.path: List[Tuple[int, int]] = None  # This is expressed in game world coordinates (can be negative)
        self.global_path_finder: GlobalPathFinder = global_path_finder

    def update_path_towards_target(self, agent_entity: WorldEntity, game_state: GameState, target_entity: WorldEntity):
        agent_cell = _translate_world_position_to_cell(agent_entity.get_position(),
                                                       game_state.game_world.entire_world_area)
        target_cell = _translate_world_position_to_cell(target_entity.get_position(),
                                                        game_state.game_world.entire_world_area)

        agent_cell_size = (agent_entity.pygame_collision_rect.w // GRID_CELL_WIDTH + 1,
                           agent_entity.pygame_collision_rect.h // GRID_CELL_WIDTH + 1)
        self.global_path_finder.register_entity_size(agent_cell_size)
        path_with_cells = self.global_path_finder.run(agent_cell_size, agent_cell, target_cell)
        if path_with_cells:
            # Note: Cells are expressed in non-negative values (and need to be translated to game world coordinates)
            path = [_translate_cell_to_world_position(cell, game_state.game_world.entire_world_area) for cell in
                    path_with_cells]
            if DEBUG_RENDER_PATHFINDING:
                _add_visual_lines_along_path(game_state, path)
            self.path = path
        else:
            self.path = None

    def get_next_waypoint_along_path(self, agent_entity: WorldEntity) -> Optional[Tuple[int, int]]:
        if self.path:
            # -----------------------------------------------
            # 1: Remove first waypoint if close enough to it
            # -----------------------------------------------
            # TODO: Does this cause problems for specific entity sizes / movement speeds?
            closeness_margin = 50
            if is_x_and_y_within_distance(agent_entity.get_position(), self.path[0], closeness_margin):
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
                dir_to_waypoint_0 = get_directions_to_position(agent_entity, self.path[0])[0]
                dir_to_waypoint_1 = get_directions_to_position(agent_entity, self.path[1])[0]
                if dir_to_waypoint_0 == get_opposite_direction(dir_to_waypoint_1):
                    # print("Not gonna go back. Popping " + str(self.path[0]))
                    self.path.pop(0)
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
    def get_dir_towards_considering_collisions(game_state: GameState, agent_entity: WorldEntity,
                                               destination: Tuple[int, int]) -> Optional[Direction]:
        if DEBUG_RENDER_PATHFINDING:
            _add_visual_line_to_next_waypoint(destination, agent_entity, game_state)
        directions = get_directions_to_position(agent_entity, destination)
        if directions:
            # TODO Refactor collision checking
            if _would_collide_with_dir(directions[0], agent_entity, game_state):
                if len(directions) > 1 and directions[1]:
                    # print("Colliding in main direction (" + str(directions[0]) + ")")
                    if not _would_collide_with_dir(directions[1], agent_entity, game_state):
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


def _add_visual_line_to_next_waypoint(destination, agent_entity: WorldEntity, game_state: GameState):
    start = _get_middle_of_cell_from_position(agent_entity.get_position())
    end = _get_middle_of_cell_from_position(destination)
    game_state.game_world.visual_effects.append(VisualLine((150, 150, 150), start, end, Millis(100), 2))


def _add_visual_lines_along_path(game_state: GameState, path):
    for i in range(len(path) - 1):
        current_pos = path[i]
        next_pos = path[i + 1]
        game_state.game_world.visual_effects.append(
            VisualRect((100, 150, 150),
                       _get_middle_of_cell_from_position(current_pos), 7, 10,
                       Millis(DEBUG_PATHFINDER_INTERVAL), 1))
        game_state.game_world.visual_effects.append(
            VisualLine((250, 250, 250),
                       _get_middle_of_cell_from_position(current_pos),
                       _get_middle_of_cell_from_position(next_pos),
                       Millis(DEBUG_PATHFINDER_INTERVAL), 1))


def _get_middle_of_cell_from_position(world_position: Tuple[int, int]) -> Tuple[int, int]:
    return world_position[0] + GRID_CELL_WIDTH // 2, \
           world_position[1] + GRID_CELL_WIDTH // 2


def _would_collide_with_dir(direction: Direction, agent_entity: WorldEntity, game_state: GameState):
    # TODO Is this too naive to work?
    future_time = Millis(100)
    future_pos = agent_entity.get_new_position_according_to_other_dir_and_speed(direction, future_time)
    future_pos_within_world = game_state.game_world.get_within_world(
        future_pos, (agent_entity.pygame_collision_rect.w, agent_entity.pygame_collision_rect.h))
    would_collide = game_state.game_world.would_entity_collide_if_new_pos(agent_entity, future_pos_within_world)
    return would_collide


def _translate_world_position_to_cell(position: Tuple[int, int], entire_world_area: Rect) -> Tuple[int, int]:
    return (int((position[0] - entire_world_area.x + GRID_CELL_WIDTH / 2) // GRID_CELL_WIDTH),
            int((position[1] - entire_world_area.y + GRID_CELL_WIDTH / 2) // GRID_CELL_WIDTH))


def _translate_cell_to_world_position(cell: Tuple[int, int], entire_world_area: Rect) -> Tuple[int, int]:
    return (cell[0] * GRID_CELL_WIDTH + entire_world_area.x,
            cell[1] * GRID_CELL_WIDTH + entire_world_area.y)
