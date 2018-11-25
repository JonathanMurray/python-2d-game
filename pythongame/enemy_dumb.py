import random

from pythongame.core.common import Millis, get_opposite_direction, \
    get_perpendicular_directions, EnemyType, Sprite
from pythongame.core.enemy_behavior import register_enemy_behavior, AbstractEnemyMind
from pythongame.core.enemy_pathfinding import EnemyPathfinder
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, register_enemy_data, \
    EnemyData
from pythongame.core.game_state import GameState, Enemy, WorldEntity


class DumbEnemyMind(AbstractEnemyMind):
    def __init__(self):
        self._state = "INIT"
        self._time_since_state_check = 0
        self._state_check_interval = 750
        self._flight_duration = 3000
        self._time_since_started_fleeing = 0

        self._update_path_interval = 900
        self._time_since_updated_path = self._update_path_interval
        self.pathfinder = EnemyPathfinder()
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_state_check += time_passed
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
            direction = self._get_direction(enemy, game_state, self.next_waypoint)
            if direction:
                enemy_entity.set_moving_in_dir(direction)
            else:
                enemy_entity.set_not_moving()

        if self._state == "FLEEING":
            self._time_since_started_fleeing += time_passed
        if self._time_since_state_check > self._state_check_interval:
            self._time_since_state_check = 0
            is_low_health = enemy.health <= enemy.max_health / 2
            if self._state == "INIT" and is_low_health:
                self._state = "FLEEING"
            if self._state == "FLEEING" and self._time_since_started_fleeing > self._flight_duration:
                self._state = "STOPPED_FLEEING"

    def _get_direction(self, enemy, game_state, next_waypoint):
        if next_waypoint:
            direction = self.pathfinder.get_dir_towards_considering_collisions(
                game_state, enemy.world_entity, next_waypoint)
            if direction:
                if self._state == "FLEEING":
                    direction = get_opposite_direction(direction)
                if random.random() < 0.2:
                    direction = random.choice(get_perpendicular_directions(direction))
                return direction
        return None


def register_dumb_enemy():
    size = (28, 28)
    register_enemy_data(EnemyType.DUMB, EnemyData(Sprite.ENEMY, size, 5, 0.02))
    register_enemy_behavior(EnemyType.DUMB, DumbEnemyMind)
    register_entity_sprite_initializer(Sprite.ENEMY, SpriteInitializer("resources/graphics/enemy.png", size))
