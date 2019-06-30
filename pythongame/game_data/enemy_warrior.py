from pythongame.core.common import Millis, is_x_and_y_within_distance, NpcType, Sprite, Direction
from pythongame.core.damage_interactions import deal_npc_damage
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.loot import LootTable, LootEntry, LootGroup
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.visual_effects import VisualLine


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._attack_interval = 1000
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 600
        self._time_since_updated_path = self._update_path_interval
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
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()

        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                target_center_pos = target.entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, target_center_pos, 80):
                    damage_amount = 6
                    deal_npc_damage(damage_amount, game_state, target)
                    game_state.visual_effects.append(
                        VisualLine((220, 0, 0), enemy_position, target_center_pos, Millis(100), 3))


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_warrior_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_WARRIOR
    npc_type = NpcType.WARRIOR
    movement_speed = 0.12
    health = 32
    exp_reward = 20
    loot = LootTable([LootGroup(1, [LootEntry.money(1), LootEntry.money(2)], 0.2)])
    register_npc_data(npc_type,
                      NpcData(sprite, size, health, 0, movement_speed, exp_reward, True, False, None, None, loot))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/human_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)

    sheet_x = 6
    indices_by_dir = {
        Direction.DOWN: [(sheet_x, 0), (sheet_x + 1, 0), (sheet_x + 2, 0), (sheet_x + 1, 0)],
        Direction.LEFT: [(sheet_x, 1), (sheet_x + 1, 1), (sheet_x + 2, 1), (sheet_x + 1, 1)],
        Direction.RIGHT: [(sheet_x, 2), (sheet_x + 1, 2), (sheet_x + 2, 2), (sheet_x + 1, 2)],
        Direction.UP: [(sheet_x, 3), (sheet_x + 1, 3), (sheet_x + 2, 3), (sheet_x + 1, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
