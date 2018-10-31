import random

from common import *
from game_data import ENEMY_PROJECTILE_SIZE
from game_state import WorldEntity, Projectile
from projectiles import create_projectile_controller


def create_enemy_mind(enemy_behavior):
    if enemy_behavior == EnemyBehavior.DUMB:
        return DumbEnemyMind()
    elif enemy_behavior == EnemyBehavior.SMART:
        return SmartEnemyMind()
    elif enemy_behavior == EnemyBehavior.MAGE:
        return MageEnemyMind()
    else:
        raise Exception("Unhandled behavior: " + str(enemy_behavior))


class DumbEnemyMind:
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 750
        self._flight_duration = 3000
        self._state = "INIT"
        self._time_since_started_fleeing = 0

    def control_enemy(self, game_state, enemy, player_entity, is_player_invisible, time_passed):
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
                direction = _get_direction_between(enemy.world_entity, player_entity)
                if self._state == "FLEEING":
                    direction = _get_opposite_direction(direction)
                if random.random() < 0.2:
                    direction = random.choice(_get_perpendicular_directions(direction))
            enemy.world_entity.set_moving_in_dir(direction)


class SmartEnemyMind:
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 350
        self._time_since_firing = 0
        self._update_firing_cooldown()
        self._pause_after_fire_duration = 700

    def control_enemy(self, game_state, enemy, player_entity, is_player_invisible, time_passed):
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
                    projectile_pos = (center_position[0] - ENEMY_PROJECTILE_SIZE[0] / 2,
                                      center_position[1] - ENEMY_PROJECTILE_SIZE[1] / 2)
                    entity = WorldEntity(projectile_pos, ENEMY_PROJECTILE_SIZE, Sprite.POISONBALL,
                                         enemy.world_entity.direction, 2)
                    projectile = Projectile(entity, False, create_projectile_controller(ProjectileType.ENEMY_POISON))
                    game_state.projectile_entities.append(projectile)
                else:
                    direction = _get_direction_between(enemy.world_entity, player_entity)
                    enemy.world_entity.set_moving_in_dir(direction)

    def _update_firing_cooldown(self):
        self._firing_cooldown = 1500 + random.random() * 5000


class MageEnemyMind:
    def __init__(self):
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_firing = 0
        self._firing_cooldown = 3000
        self._time_since_healing = 0
        self._healing_cooldown = 5000

    def control_enemy(self, game_state, enemy, player_entity, is_player_invisible, time_passed):
        self._time_since_decision += time_passed
        self._time_since_firing += time_passed
        self._time_since_healing += time_passed
        if self._time_since_firing > self._firing_cooldown:
            self._time_since_firing = 0
            center_position = enemy.world_entity.get_center_position()
            projectile_pos = (center_position[0] - ENEMY_PROJECTILE_SIZE[0] / 2,
                              center_position[1] - ENEMY_PROJECTILE_SIZE[1] / 2)
            entities = [WorldEntity(projectile_pos, ENEMY_PROJECTILE_SIZE, Sprite.POISONBALL, direction, 2)
                        for direction in _get_all_directions()]
            projectiles = [Projectile(entity, False, create_projectile_controller(ProjectileType.ENEMY_POISON))
                           for entity in entities]
            game_state.projectile_entities += projectiles

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            enemy_pos = enemy.world_entity.get_center_position()
            healing_range = 200
            nearby_hurt_enemies = [e for e in game_state.enemies if abs(e.world_entity.x - enemy_pos[0]) < healing_range
                                   and abs(e.world_entity.y - enemy_pos[1]) < healing_range and e != enemy
                                   and e.health < e.max_health]
            if nearby_hurt_enemies:
                nearby_hurt_enemies[0].gain_health(5)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                enemy.world_entity.set_moving_in_dir(direction)
            else:
                enemy.world_entity.set_not_moving()


def _get_direction_between(from_entity, to_entity):
    dx = to_entity.x - from_entity.x
    dy = to_entity.y - from_entity.y
    if abs(dx) > abs(dy):
        if dx > 0:
            direction = Direction.RIGHT
        else:
            direction = Direction.LEFT
    else:
        if dy < 0:
            direction = Direction.UP
        else:
            direction = Direction.DOWN
    return direction


def _get_perpendicular_directions(direction):
    if direction == direction.LEFT or direction == direction.RIGHT:
        return [Direction.UP, Direction.DOWN]
    else:
        return [Direction.LEFT, Direction.RIGHT]


def _get_opposite_direction(direction):
    if direction == direction.LEFT:
        return direction.RIGHT
    if direction == direction.RIGHT:
        return direction.LEFT
    if direction == direction.UP:
        return direction.DOWN
    if direction == direction.DOWN:
        return direction.UP


def _get_all_directions():
    return [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
