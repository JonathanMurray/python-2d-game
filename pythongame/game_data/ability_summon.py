import random

from pythongame.core.ability_effects import register_ability_effect
from pythongame.core.common import get_position_from_center_position, Sprite, AbilityType, Millis, \
    sum_of_vectors, EnemyType, get_perpendicular_directions
from pythongame.core.enemy_behaviors import register_enemy_behavior, AbstractEnemyMind
from pythongame.core.enemy_creation import create_enemy
from pythongame.core.game_data import register_ability_data, AbilityData, UiIconSprite, \
    ENEMIES, register_enemy_data, EnemyData
from pythongame.core.game_state import GameState, WorldEntity, Enemy
from pythongame.core.pathfinding.enemy_pathfinding import EnemyPathfinder
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


def _apply_ability(game_state: GameState):
    player_entity = game_state.player_entity

    # TODO don't depend on ENEMIES (summon != enemy)
    relative_pos = (random.randint(-80, 80), random.randint(-80, 80))
    summon_center_pos = sum_of_vectors(player_entity.get_center_position(), relative_pos)
    summon_pos = get_position_from_center_position(summon_center_pos, ENEMIES[EnemyType.MUMMY].size)
    summon = create_enemy(EnemyType.PLAYER_SUMMON, summon_pos)
    if not game_state.would_entity_collide_if_new_pos(summon.world_entity, summon_pos):
        game_state.enemies.append(summon)


class EnemyMind(AbstractEnemyMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = EnemyPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def control_enemy(self, game_state: GameState, enemy: Enemy, player_entity: WorldEntity, is_player_invisible: bool,
                      time_passed: Millis):
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
                if random.random() < 0.1 and direction:
                    direction = random.choice(get_perpendicular_directions(direction))
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_summon_ability():
    ability_type = AbilityType.SUMMON
    register_ability_effect(ability_type, _apply_ability)
    ui_icon_sprite = UiIconSprite.ITEM_STAFF_OF_FIRE
    register_ability_data(ability_type, AbilityData("Summon", ui_icon_sprite, 3, Millis(300), "Summon TODO"))

    summoned_enemy_type = EnemyType.PLAYER_SUMMON
    register_enemy_data(summoned_enemy_type, EnemyData(Sprite.ENEMY_MUMMY, (42, 42), 10, 0, 0.05, 0))
    register_enemy_behavior(summoned_enemy_type, EnemyMind)
