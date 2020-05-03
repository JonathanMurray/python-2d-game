import random

from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import Millis, NpcType, Sprite, Direction, BuffType, HeroStat, SoundId, LootTableId
from pythongame.core.damage_interactions import deal_npc_damage, DamageType
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_buff_text
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.math import is_x_and_y_within_distance
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualLine
from pythongame.core.world_entity import WorldEntity

DAMAGE_MIN = 6
DAMAGE_MAX = 12
SLOW_AMOUNT = 0.35
SLOW_BUFF_TYPE = BuffType.SLOWED_BY_ICE_WITCH


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._base_attack_interval = 4000
        self._attack_interval = None
        self.randomize_attack_interval()
        self._time_since_attack = self._attack_interval
        self._update_path_interval = 600
        self._time_since_updated_path = self._update_path_interval
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval

    def randomize_attack_interval(self):
        self._attack_interval = self._base_attack_interval + random.randint(-250, 250)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return
        self._time_since_attack += time_passed
        self._time_since_updated_path += time_passed
        self._time_since_reevaluated += time_passed

        enemy_entity = npc.world_entity
        target: EnemyTarget = get_target(enemy_entity, game_state)

        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if not is_player_invisible:
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
            if not is_player_invisible:
                enemy_position = enemy_entity.get_center_position()
                target_center_pos = target.entity.get_center_position()
                if is_x_and_y_within_distance(enemy_position, target_center_pos, 200):
                    self._time_since_attack = 0
                    self.randomize_attack_interval()
                    play_sound(SoundId.ENEMY_ATTACK_ICE_WITCH)
                    damage = random.randint(DAMAGE_MIN, DAMAGE_MAX)
                    deal_npc_damage(damage, DamageType.MAGIC, game_state, enemy_entity, npc, target)
                    game_state.game_world.visual_effects += [
                        (VisualLine((100, 100, 200), enemy_position, target_center_pos, Millis(120), 3)),
                        (VisualLine((150, 150, 250), enemy_position, target_center_pos, Millis(240), 2))]
                    chance_to_resist_slow = game_state.player_state.get_effective_movement_impairing_resist_chance()
                    # TODO It's error-prone that we have to check this for every negative debuff that can slow player
                    if random.random() > chance_to_resist_slow:
                        game_state.player_state.gain_buff_effect(get_buff_effect(SLOW_BUFF_TYPE), Millis(1500))


class SlowedByIceWitch(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(SLOW_BUFF_TYPE, {HeroStat.MOVEMENT_SPEED: -SLOW_AMOUNT})


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


def register_ice_witch_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_ICE_WITCH
    npc_type = NpcType.ICE_WITCH
    movement_speed = 0.07
    health = 50
    exp_reward = 40
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LootTableId.LEVEL_6,
                             SoundId.DEATH_ICE_WITCH)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_ice_witch.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)

    sheet_x = 0
    indices_by_dir = {
        Direction.DOWN: [(sheet_x, 0), (sheet_x + 1, 0), (sheet_x + 2, 0), (sheet_x + 1, 0)],
        Direction.LEFT: [(sheet_x, 1), (sheet_x + 1, 1), (sheet_x + 2, 1), (sheet_x + 1, 1)],
        Direction.RIGHT: [(sheet_x, 2), (sheet_x + 1, 2), (sheet_x + 2, 2), (sheet_x + 1, 2)],
        Direction.UP: [(sheet_x, 3), (sheet_x + 1, 3), (sheet_x + 2, 3), (sheet_x + 1, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_buff_effect(SLOW_BUFF_TYPE, SlowedByIceWitch)
    register_buff_text(SLOW_BUFF_TYPE, "Frozen")
