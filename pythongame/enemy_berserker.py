import random

from pythongame.common import Millis, random_direction, is_x_and_y_within_distance, get_direction_between, \
    get_perpendicular_directions, EnemyBehavior, Sprite
from pythongame.enemy_behavior import register_enemy_behavior
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, ENEMY_BERSERKER_SIZE
from pythongame.game_state import GameState, Enemy, WorldEntity
from pythongame.visual_effects import VisualLine, create_visual_damage_text


class BerserkerEnemyMind:
    def __init__(self):
        self._decision_interval = 750
        self._time_since_decision = self._decision_interval
        self._attack_interval = 1500
        self._time_since_attack = self._attack_interval

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_attack += time_passed
        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if is_player_invisible:
                direction = random_direction()
            else:
                direction = get_direction_between(enemy.world_entity, player_entity)
                if random.random() < 0.2:
                    direction = random.choice(get_perpendicular_directions(direction))
            enemy.world_entity.set_moving_in_dir(direction)
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


def register_berserker_enemy():
    register_enemy_behavior(EnemyBehavior.BERSERKER, BerserkerEnemyMind)
    register_entity_sprite_initializer(
        Sprite.ENEMY_BERSERKER, SpriteInitializer("resources/orc_berserker.png", ENEMY_BERSERKER_SIZE))
