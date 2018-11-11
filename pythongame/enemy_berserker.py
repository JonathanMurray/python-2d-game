from pythongame.common import Millis, is_x_and_y_within_distance, EnemyType, Sprite
from pythongame.enemy_behavior import register_enemy_behavior, AbstractEnemyMind
from pythongame.enemy_pathfinding import EnemyPathfinder
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, register_enemy_data, EnemyData
from pythongame.game_state import GameState, Enemy, WorldEntity
from pythongame.visual_effects import VisualLine, create_visual_damage_text


class BerserkerEnemyMind(AbstractEnemyMind):
    def __init__(self):
        self._attack_interval = 1500
        self._time_since_attack = self._attack_interval
        self._pathfinder_interval = 900
        self._time_since_pathfinder = self._pathfinder_interval
        self.pathfinder = EnemyPathfinder()

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_pathfinder += time_passed

        just_found_path = False
        if self._time_since_pathfinder > self._pathfinder_interval:
            self._time_since_pathfinder = 0
            self.pathfinder.update_path(enemy, game_state)
            just_found_path = True

        self.pathfinder.move_enemy_along_path(enemy, game_state, just_found_path)

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
    size = (50, 50)
    register_enemy_data(EnemyType.BERSERKER, EnemyData(Sprite.ENEMY_BERSERKER, size, 5, 0.1))
    register_enemy_behavior(EnemyType.BERSERKER, BerserkerEnemyMind)
    register_entity_sprite_initializer(
        Sprite.ENEMY_BERSERKER, SpriteInitializer("resources/orc_berserker.png", size))
