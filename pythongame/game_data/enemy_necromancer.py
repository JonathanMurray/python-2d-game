import random

from pythongame.core.common import Millis, random_direction, EnemyType, Sprite, \
    is_x_and_y_within_distance, Direction, sum_of_vectors, get_position_from_center_position
from pythongame.core.enemy_behaviors import register_enemy_behavior, AbstractEnemyMind
from pythongame.core.enemy_creation import create_enemy
from pythongame.core.game_data import register_enemy_data, \
    EnemyData, SpriteSheet, register_entity_sprite_map, ENEMIES
from pythongame.core.game_state import GameState, Enemy, WorldEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import VisualLine, VisualCircle

SPRITE = Sprite.ENEMY_NECROMANCER
ENEMY_TYPE = EnemyType.NECROMANCER


class EnemyMind(AbstractEnemyMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_summoning = 0
        self._summoning_cooldown = 8000
        self._time_since_healing = 0
        self._healing_cooldown = 5000

    def control_enemy(self, game_state: GameState, enemy: Enemy, _player_entity: WorldEntity,
                      _is_player_invisible: bool, time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_summoning += time_passed
        self._time_since_healing += time_passed
        if self._time_since_summoning > self._summoning_cooldown:
            necro_center_pos = enemy.world_entity.get_center_position()
            self._time_since_summoning = 0
            relative_pos_from_summoner = (random.randint(-150, 150), random.randint(-150, 150))
            mummy_center_pos = sum_of_vectors(necro_center_pos, relative_pos_from_summoner)
            mummy_pos = get_position_from_center_position(mummy_center_pos, ENEMIES[EnemyType.MUMMY].size)
            mummy_enemy = create_enemy(EnemyType.MUMMY, mummy_pos)
            if not game_state.would_entity_collide_if_new_pos(mummy_enemy.world_entity, mummy_pos):
                game_state.enemies.append(mummy_enemy)
                game_state.visual_effects.append(VisualCircle((80, 150, 100), necro_center_pos, 40, 70, Millis(120), 3))
                game_state.visual_effects.append(VisualCircle((80, 150, 100), mummy_center_pos, 40, 70, Millis(120), 3))

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            necro_center_pos = enemy.world_entity.get_center_position()
            nearby_hurt_enemies = [e for e in game_state.enemies
                                   if is_x_and_y_within_distance(necro_center_pos, e.world_entity.get_center_position(),
                                                                 200)
                                   and e != enemy and e.health < e.max_health]
            if nearby_hurt_enemies:
                healing_target = nearby_hurt_enemies[0]
                healing_target.gain_health(5)
                healing_target_pos = healing_target.world_entity.get_center_position()
                visual_line = VisualLine((80, 200, 150), necro_center_pos, healing_target_pos, Millis(350), 3)
                game_state.visual_effects.append(visual_line)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                enemy.world_entity.set_moving_in_dir(direction)
            else:
                enemy.world_entity.set_not_moving()


def register_necromancer_enemy():
    size = (50, 60)
    health = 25
    register_enemy_data(ENEMY_TYPE, EnemyData(SPRITE, size, health, 0, 0.02))
    register_enemy_behavior(ENEMY_TYPE, EnemyMind)

    enemy_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    enemy_original_sprite_size = (32, 32)
    enemy_scaled_sprite_size = (50, 60)
    enemy_indices_by_dir = {
        Direction.DOWN: [(x, 0) for x in range(9, 12)],
        Direction.LEFT: [(x, 1) for x in range(9, 12)],
        Direction.RIGHT: [(x, 2) for x in range(9, 12)],
        Direction.UP: [(x, 3) for x in range(9, 12)]
    }
    register_entity_sprite_map(SPRITE, enemy_sprite_sheet, enemy_original_sprite_size,
                               enemy_scaled_sprite_size, enemy_indices_by_dir, (0, 0))
