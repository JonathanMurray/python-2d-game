from typing import Tuple

from pythongame.common import Millis, is_x_and_y_within_distance, EnemyType, Sprite, \
    get_directions_to_position, get_opposite_direction
from pythongame.enemy_behavior import register_enemy_behavior, AbstractEnemyMind
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, register_enemy_data, EnemyData
from pythongame.game_state import GameState, Enemy, WorldEntity, GRID_CELL_WIDTH
from pythongame.grid_astar_pathfinder import run_pathfinder
from pythongame.visual_effects import VisualLine, create_visual_damage_text


DEBUG_RENDER_PATHFINDING = False


class BerserkerEnemyMind(AbstractEnemyMind):
    def __init__(self):
        self._attack_interval = 1500
        self._time_since_attack = self._attack_interval
        self._pathfinder_interval = 900
        self._time_since_pathfinder = self._pathfinder_interval
        self.path = None

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_pathfinder += time_passed

        just_found_path = False
        if self._time_since_pathfinder > self._pathfinder_interval:
            self._time_since_pathfinder = 0
            self.path = self._get_path(enemy, player_entity, game_state)
            just_found_path = True
            if not self.path:
                print("no path found. stopping.")
                enemy.world_entity.set_not_moving()

        if self.path:
            self._deal_with_path(enemy, game_state, just_found_path)

        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            if not is_player_invisible:
                enemy_position = enemy.world_entity.get_center_position()
                player_center_pos = game_state.player_entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, player_center_pos, 80):
                    damage_amount = 12
                    game_state.player_state.lose_health(damage_amount)
                    game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, damage_amount))
                    game_state.visual_effects.append(
                        VisualLine((220, 0, 0), enemy_position, player_center_pos, Millis(100), 3))

    def _move_towards(self, game_state: GameState, enemy: Enemy, destination: Tuple[int, int]):
        enemy_entity = enemy.world_entity
        if DEBUG_RENDER_PATHFINDING:
            game_state.visual_effects.append(
                VisualLine((0, 0, 150), (enemy_entity.x, enemy_entity.y),
                           destination, Millis(200), 2))
        directions = get_directions_to_position(enemy_entity, destination)
        if directions:
            #TODO Refactor collision checking
            enemy_entity.set_moving_in_dir(directions[0])
            future_pos = enemy_entity.get_new_position_according_to_dir_and_speed(100)
            future_pos_within_world = game_state.get_within_world(future_pos, (enemy_entity.w, enemy_entity.h))
            would_collide = game_state.would_entity_collide_if_new_pos(enemy_entity, future_pos_within_world)
            if would_collide:
                if len(directions) > 1 and directions[1]:
                    print("Colliding in main direction (" + str(directions[0]) + ") so will use " + str(directions[1]))
                    enemy_entity.set_moving_in_dir(directions[1])
                else:
                    print("Colliding in main direction (" + str(directions[0]) + ") but there is no other choice")


    def _get_path(self, enemy, player_entity, game_state):
        enemy_position = enemy.world_entity.get_center_position()
        enemy_cell = (enemy_position[0] // GRID_CELL_WIDTH, enemy_position[1] // GRID_CELL_WIDTH)
        player_position = player_entity.get_center_position()
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
                                   path[i + 1], Millis(self._pathfinder_interval), 3))
            return path
        else:
            return None

    def _deal_with_path(self, enemy, game_state, just_found_path):
        if is_x_and_y_within_distance((enemy.world_entity.x, enemy.world_entity.y),
                                      self.path[0], 15):
            self.path.pop(0)
            if self.path:
                self._move_towards(game_state, enemy, self.path[0])
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
                    self._move_towards(game_state, enemy, self.path[0])
                else:
                    enemy.world_entity.set_not_moving()
        if just_found_path:
            if self.path:
                self._move_towards(game_state, enemy, self.path[0])


def register_berserker_enemy():
    size = (50, 50)
    register_enemy_data(EnemyType.BERSERKER, EnemyData(Sprite.ENEMY_BERSERKER, size, 5, 0.1))
    register_enemy_behavior(EnemyType.BERSERKER, BerserkerEnemyMind)
    register_entity_sprite_initializer(
        Sprite.ENEMY_BERSERKER, SpriteInitializer("resources/orc_berserker.png", size))
