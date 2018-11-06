import random

from pythongame.common import Millis, random_direction, EnemyBehavior, Sprite, \
    get_position_from_center_position, ProjectileType, is_x_and_y_within_distance, get_all_directions
from pythongame.enemy_behavior import register_enemy_behavior
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, ENEMY_PROJECTILE_SIZE, \
    ENEMY_MAGE_ENTITY_SIZE
from pythongame.game_state import GameState, Enemy, WorldEntity, Projectile
from pythongame.projectile_enemy_poison import register_enemy_poison_projectile
from pythongame.projectiles import create_projectile_controller
from pythongame.visual_effects import VisualLine


class MageEnemyMind:
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_firing = 0
        self._firing_cooldown = 3000
        self._time_since_healing = 0
        self._healing_cooldown = 5000

    def control_enemy(self, game_state: GameState, enemy: Enemy, _player_entity: WorldEntity,
                      _is_player_invisible: bool, time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_firing += time_passed
        self._time_since_healing += time_passed
        if self._time_since_firing > self._firing_cooldown:
            self._time_since_firing = 0
            center_position = enemy.world_entity.get_center_position()
            projectile_pos = get_position_from_center_position(center_position, ENEMY_PROJECTILE_SIZE)
            entities = [WorldEntity(projectile_pos, ENEMY_PROJECTILE_SIZE, Sprite.POISONBALL, direction, 0.1)
                        for direction in get_all_directions()]
            projectiles = [Projectile(entity, create_projectile_controller(ProjectileType.ENEMY_POISON))
                           for entity in entities]
            game_state.projectile_entities += projectiles

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            mage_pos = enemy.world_entity.get_center_position()
            nearby_hurt_enemies = [e for e in game_state.enemies
                                   if is_x_and_y_within_distance(mage_pos, e.world_entity.get_center_position(), 200)
                                   and e != enemy and e.health < e.max_health]
            if nearby_hurt_enemies:
                healing_target = nearby_hurt_enemies[0]
                healing_target.gain_health(5)
                healing_target_pos = healing_target.world_entity.get_center_position()
                visual_line = VisualLine((80, 80, 250), mage_pos, healing_target_pos, Millis(350), 3)
                game_state.visual_effects.append(visual_line)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                enemy.world_entity.set_moving_in_dir(direction)
            else:
                enemy.world_entity.set_not_moving()


def register_mage_enemy():
    register_enemy_behavior(EnemyBehavior.MAGE, MageEnemyMind)
    register_entity_sprite_initializer(
        Sprite.ENEMY_MAGE, SpriteInitializer("resources/enemy_mage.png", ENEMY_MAGE_ENTITY_SIZE))
    register_enemy_poison_projectile()
