import random

from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Millis, EnemyType, Sprite, \
    get_position_from_center_position, ProjectileType, BuffType, Direction, get_perpendicular_directions, \
    translate_in_direction
from pythongame.core.damage_interactions import deal_damage_to_player
from pythongame.core.enemy_behaviors import register_enemy_behavior, AbstractEnemyMind
from pythongame.core.game_data import register_enemy_data, \
    EnemyData, register_buff_text, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, Enemy, WorldEntity, Projectile
from pythongame.core.pathfinding.enemy_pathfinding import EnemyPathfinder
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.visual_effects import VisualCircle, VisualText

BUFF_TYPE = BuffType.ENEMY_GOBLIN_WARLOCK_BURNT
PROJECTILE_TYPE = ProjectileType.ENEMY_GOBLIN_WARLOCK
PROJECTILE_SPRITE = Sprite.PROJECTILE_ENEMY_GOBLIN_WARLOCK
PROJECTILE_SIZE = (20, 20)
COLOR_SPEECH = (200, 100, 70)


class EnemyMind(AbstractEnemyMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_attack_interval()
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = EnemyPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval
        self._update_speech_interval()
        self._time_since_speech = 0

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed
        self._time_since_speech += time_passed

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
                if random.random() < 0.1 and direction:
                    direction = random.choice(get_perpendicular_directions(direction))
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()

        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            self._update_attack_interval()
            enemy.world_entity.set_not_moving()
            center_position = enemy.world_entity.get_center_position()
            distance_from_enemy = 35
            projectile_pos = translate_in_direction(
                get_position_from_center_position(center_position, PROJECTILE_SIZE),
                enemy.world_entity.direction, distance_from_enemy)
            projectile_speed = 0.07
            projectile_entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, PROJECTILE_SPRITE,
                                            enemy.world_entity.direction, projectile_speed)
            projectile = Projectile(projectile_entity, create_projectile_controller(PROJECTILE_TYPE))
            game_state.projectile_entities.append(projectile)

        if self._time_since_speech > self._speech_interval:
            self._time_since_speech = 0
            self._update_speech_interval()
            speech_text_pos = (enemy_entity.x - 20, enemy_entity.y - 30)
            speech_line = random.choice(["EHEHEHE", "HOT! SO HOT!!"])
            game_state.visual_effects.append(
                VisualText(speech_line, COLOR_SPEECH, speech_text_pos, speech_text_pos, Millis(3500)))

    def _update_attack_interval(self):
        self._attack_interval = 2000 + random.random() * 4000

    def _update_speech_interval(self):
        self._speech_interval = 8000 + random.random() * 10000


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState):
        deal_damage_to_player(game_state, 1)
        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.ENEMY_GOBLIN_WARLOCK_BURNT), Millis(5000))
        game_state.visual_effects.append(VisualCircle((180, 50, 50), game_state.player_entity.get_center_position(),
                                                      25, 50, Millis(100), 0))
        return True


class Burnt(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 500:
            self._time_since_graphics = 0
            deal_damage_to_player(game_state, 1)
            game_state.visual_effects.append(VisualCircle((180, 50, 50), game_state.player_entity.get_center_position(),
                                                          10, 20, Millis(50), 0, game_state.player_entity))

    def get_buff_type(self):
        return BUFF_TYPE


def register_goblin_warlock_enemy():
    enemy_size = (42, 42)
    enemy_sprite = Sprite.ENEMY_GOBLIN_WARLOCK
    enemy_type = EnemyType.GOBLIN_WARLOCK

    health = 21
    register_enemy_data(enemy_type, EnemyData(enemy_sprite, enemy_size, health, 0, 0.032))
    register_enemy_behavior(enemy_type, EnemyMind)

    enemy_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    enemy_original_sprite_size = (32, 32)
    enemy_scaled_sprite_size = (48, 48)
    enemy_indices_by_dir = {
        Direction.DOWN: [(0, 4), (1, 4), (2, 4)],
        Direction.LEFT: [(0, 5), (1, 5), (2, 5)],
        Direction.RIGHT: [(0, 6), (1, 6), (2, 6)],
        Direction.UP: [(0, 7), (1, 7), (2, 7)]
    }
    register_entity_sprite_map(enemy_sprite, enemy_sprite_sheet, enemy_original_sprite_size, enemy_scaled_sprite_size,
                               enemy_indices_by_dir, (-3, -3))

    register_projectile_controller(ProjectileType.ENEMY_GOBLIN_WARLOCK, ProjectileController)

    projectile_sprite_sheet = SpriteSheet("resources/graphics/goblin_fireball_entity.png")
    projectile_original_sprite_size = (132, 156)
    projectile_scaled_sprite_size = (20, 20)
    projectile_indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)]
    }
    projectile_sprite = Sprite.PROJECTILE_ENEMY_GOBLIN_WARLOCK
    register_entity_sprite_map(projectile_sprite, projectile_sprite_sheet, projectile_original_sprite_size,
                               projectile_scaled_sprite_size, projectile_indices_by_dir, (0, 0))

    register_buff_effect(BUFF_TYPE, Burnt)
    register_buff_text(BUFF_TYPE, "Burnt")
