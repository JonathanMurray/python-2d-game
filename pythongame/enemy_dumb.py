import random

from pythongame.common import Millis, random_direction, get_direction_between, get_opposite_direction, \
    get_perpendicular_directions, EnemyBehavior, Sprite
from pythongame.enemy_behavior import register_enemy_behavior
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, ENEMY_ENTITY_SIZE
from pythongame.game_state import GameState, Enemy, WorldEntity


class DumbEnemyMind:
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 750
        self._flight_duration = 3000
        self._state = "INIT"
        self._time_since_started_fleeing = 0

    def control_enemy(self, _game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_decision += time_passed
        if self._state == "FLEEING":
            self._time_since_started_fleeing += time_passed
        if self._time_since_decision > self._decision_interval:
            is_low_health = enemy.health <= enemy.max_health / 2
            if self._state == "INIT" and is_low_health:
                self._state = "FLEEING"
            if self._state == "FLEEING" and self._time_since_started_fleeing > self._flight_duration:
                self._state = "STOPPED_FLEEING"

            self._time_since_decision = 0
            if is_player_invisible:
                direction = random_direction()
            else:
                direction = get_direction_between(enemy.world_entity, player_entity)
                if self._state == "FLEEING":
                    direction = get_opposite_direction(direction)
                if random.random() < 0.2:
                    direction = random.choice(get_perpendicular_directions(direction))
            enemy.world_entity.set_moving_in_dir(direction)


def register_dumb_enemy():
    register_enemy_behavior(EnemyBehavior.DUMB, DumbEnemyMind)
    register_entity_sprite_initializer(Sprite.ENEMY, SpriteInitializer("resources/enemy.png", ENEMY_ENTITY_SIZE))
