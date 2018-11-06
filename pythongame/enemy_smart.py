import random

from pythongame.common import Millis, random_direction, get_direction_between, EnemyBehavior, Sprite, \
    get_position_from_center_position, ProjectileType
from pythongame.enemy_behavior import register_enemy_behavior, AbstractEnemyMind
from pythongame.game_data import register_entity_sprite_initializer, SpriteInitializer, ENEMY_PROJECTILE_SIZE, \
    ENEMY_2_ENTITY_SIZE
from pythongame.game_state import GameState, Enemy, WorldEntity, Projectile
from pythongame.projectile_enemy_poison import register_enemy_poison_projectile
from pythongame.projectiles import create_projectile_controller


class SmartEnemyMind(AbstractEnemyMind):
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 350
        self._time_since_firing = 0
        self._update_firing_cooldown()
        self._pause_after_fire_duration = 700

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_firing += time_passed
        self._time_since_decision += time_passed
        if self._time_since_decision > self._decision_interval \
                and self._time_since_firing > self._pause_after_fire_duration:
            self._time_since_decision = 0
            if is_player_invisible:
                direction = random_direction()
                enemy.world_entity.set_moving_in_dir(direction)
            else:
                if self._time_since_firing > self._firing_cooldown:
                    self._time_since_firing = 0
                    self._update_firing_cooldown()
                    enemy.world_entity.set_not_moving()
                    center_position = enemy.world_entity.get_center_position()
                    projectile_pos = get_position_from_center_position(center_position, ENEMY_PROJECTILE_SIZE)
                    entity = WorldEntity(projectile_pos, ENEMY_PROJECTILE_SIZE, Sprite.POISONBALL,
                                         enemy.world_entity.direction, 0.1)
                    projectile = Projectile(entity, create_projectile_controller(ProjectileType.ENEMY_POISON))
                    game_state.projectile_entities.append(projectile)
                else:
                    direction = get_direction_between(enemy.world_entity, player_entity)
                    enemy.world_entity.set_moving_in_dir(direction)

    def _update_firing_cooldown(self):
        self._firing_cooldown = 1500 + random.random() * 5000


def register_smart_enemy():
    register_enemy_behavior(EnemyBehavior.SMART, SmartEnemyMind)
    register_entity_sprite_initializer(Sprite.ENEMY_2, SpriteInitializer("resources/enemy2.png", ENEMY_2_ENTITY_SIZE))
    register_enemy_poison_projectile()
