import random

from pythongame.core.common import Millis, is_x_and_y_within_distance, NpcType, Sprite, Direction, \
    get_perpendicular_directions, ConsumableType
from pythongame.core.damage_interactions import deal_npc_damage
from pythongame.core.enemy_target_selection import get_target, EnemyTarget
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    EnemyLootEntry
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, EnemyLootPicker
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.visual_effects import VisualLine


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._attack_interval = 2000
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed

        enemy_entity = npc.world_entity
        target: EnemyTarget = get_target(enemy_entity, game_state)

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            self.pathfinder.update_path_towards_target(enemy_entity, game_state, target.entity)

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
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                target_center_pos = target.entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, target_center_pos, 100):
                    damage_amount = 3
                    deal_npc_damage(damage_amount, game_state, target)
                    game_state.visual_effects.append(
                        VisualLine((220, 0, 0), enemy_position, target_center_pos, Millis(100), 3))


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_mummy_enemy():
    size = (42, 42)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_MUMMY
    npc_type = NpcType.MUMMY
    movement_speed = 0.06
    health = 12
    health_regen = 1
    loot = EnemyLootPicker([EnemyLootEntry.money(1, 0.8), EnemyLootEntry.consumable(ConsumableType.HEALTH_LESSER, 0.2)])
    register_npc_data(npc_type,
                      NpcData(sprite, size, health, health_regen, movement_speed, 10, True, False, None, None, loot))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(6, 4), (7, 4), (8, 4)],
        Direction.LEFT: [(6, 5), (7, 5), (8, 5)],
        Direction.RIGHT: [(6, 6), (7, 6), (8, 6)],
        Direction.UP: [(6, 7), (7, 7), (8, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir, (-3, -3))
