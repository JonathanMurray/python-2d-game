import random

from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import Millis, NpcType, Sprite, Direction, BuffType, LootTableId
from pythongame.core.damage_interactions import deal_damage_to_player, DamageType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.math import get_perpendicular_directions, is_x_and_y_within_distance
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualLine, VisualCircle
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE_INVULN = BuffType.INVULNERABILITY
SPEECH_DURATION = Millis(3000)
COLOR_SPEECH = (200, 100, 70)


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._attack_interval = 1000
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval
        self._shield_interval = 13000
        self._shield_duration = 5000
        self._time_since_shield = 7000

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed
        self._time_since_shield += time_passed

        enemy_entity = npc.world_entity

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            self.pathfinder.update_path_towards_target(enemy_entity, game_state, game_state.game_world.player_entity)

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

        enemy_center_pos = enemy_entity.get_center_position()

        if self._time_since_attack > self._attack_interval:
            self._time_since_attack = 0
            game_state.game_world.visual_effects.append(VisualCircle((100, 100, 100), enemy_center_pos, 180, 180,
                                                                     Millis(self._attack_interval), 1, enemy_entity))
            if not is_player_invisible:
                player_center_pos = game_state.game_world.player_entity.get_center_position()
                if is_x_and_y_within_distance(enemy_center_pos, player_center_pos, 160):
                    deal_damage_to_player(game_state, 3, DamageType.MAGIC, npc)
                    game_state.game_world.visual_effects += [
                        VisualCircle((0, 0, 0), enemy_center_pos, 25, 50, Millis(200), 2, enemy_entity),
                        VisualLine((0, 100, 0), enemy_center_pos, player_center_pos, Millis(200), 2),
                        VisualCircle((0, 100, 0), player_center_pos, 20, 40, Millis(150), 2, player_entity),
                        VisualCircle((0, 150, 0), player_center_pos, 25, 50, Millis(200), 2, player_entity),
                        VisualCircle((0, 200, 0), player_center_pos, 30, 60, Millis(300), 2, player_entity),
                    ]

        if self._time_since_shield > self._shield_interval:
            self._time_since_shield = 0

            game_state.game_world.visual_effects.append(
                VisualCircle((0, 0, 150), enemy_center_pos, 60, 20, Millis(self._shield_duration), 2, enemy_entity)
            )
            npc.gain_buff_effect(get_buff_effect(BUFF_TYPE_INVULN), Millis(self._shield_duration))


class Invuln(AbstractBuffEffect):
    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.invulnerable = True

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.invulnerable = False

    def get_buff_type(self):
        return BUFF_TYPE_INVULN


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_dark_reaper_enemy():
    size = (50, 50)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_DARK_REAPER
    npc_type = NpcType.DARK_REAPER
    movement_speed = 0.04
    health = 80
    loot = LootTableId.LEVEL_1
    register_npc_data(npc_type, NpcData.enemy(sprite, size, health, 0, movement_speed, 40, loot))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {
        Direction.DOWN: [(9, 0), (10, 0), (11, 0)],
        Direction.LEFT: [(9, 1), (10, 1), (11, 1)],
        Direction.RIGHT: [(9, 2), (10, 2), (11, 2)],
        Direction.UP: [(9, 3), (10, 3), (11, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir, (0, 0))
    register_buff_effect(BUFF_TYPE_INVULN, Invuln)
