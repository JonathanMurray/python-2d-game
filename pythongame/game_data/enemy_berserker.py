from pythongame.core.common import Millis, is_x_and_y_within_distance, EnemyType, Sprite, Direction
from pythongame.core.damage_interactions import deal_damage_to_player
from pythongame.core.enemy_behaviors import register_enemy_behavior, AbstractEnemyMind
from pythongame.core.game_data import register_enemy_data, \
    EnemyData, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, Enemy, WorldEntity
from pythongame.core.pathfinding.enemy_pathfinding import EnemyPathfinder
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import VisualLine


class BerserkerEnemyMind(AbstractEnemyMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._attack_interval = 1500
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 900
        self._time_since_updated_path = self._update_path_interval
        self.pathfinder = EnemyPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed

        enemy_entity = enemy.world_entity

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            self.pathfinder.update_path(enemy_entity, game_state)

        new_next_waypoint = self.pathfinder.get_next_waypoint_along_path(enemy_entity)

        should_update_waypoint = self.next_waypoint != new_next_waypoint
        if self._time_since_reevaluated > self._reevaluate_next_waypoint_direction_interval:
            self._time_since_reevaluated = 0
            should_update_waypoint = True

        if should_update_waypoint:
            self.next_waypoint = new_next_waypoint
            if self.next_waypoint:
                direction = self.pathfinder.get_dir_towards_considering_collisions(
                    game_state, enemy_entity, self.next_waypoint)
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()

        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                player_center_pos = game_state.player_entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, player_center_pos, 80):
                    deal_damage_to_player(game_state, 12)
                    game_state.visual_effects.append(
                        VisualLine((220, 0, 0), enemy_position, player_center_pos, Millis(100), 3))


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_berserker_enemy():
    size = (50, 50)
    register_enemy_data(EnemyType.BERSERKER, EnemyData(Sprite.ENEMY_BERSERKER, size, 5, 0, 0.1))
    register_enemy_behavior(EnemyType.BERSERKER, BerserkerEnemyMind)
    berserker_sprite_sheet = SpriteSheet("resources/graphics/skeleton_sprite_map.png")
    original_sprite_size = (32, 48)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1), (3, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2), (3, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3), (3, 3)]
    }
    register_entity_sprite_map(Sprite.ENEMY_BERSERKER, berserker_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, (0, 0))
