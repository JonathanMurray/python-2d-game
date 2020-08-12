import random
from enum import Enum

from pythongame.core.buff_effects import get_buff_effect, StunningBuffEffect, register_buff_effect
from pythongame.core.common import Millis, NpcType, Sprite, \
    Direction, SoundId, LootTableId, ProjectileType, PeriodicTimer, BuffType
from pythongame.core.damage_interactions import deal_damage_to_player, deal_npc_damage_to_npc, DamageType
from pythongame.core.game_data import NpcData
from pythongame.core.game_state import GameState, NonPlayerCharacter, Projectile
from pythongame.core.math import get_position_from_center_position, \
    translate_in_direction, get_directions_to_position
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import AbstractProjectileController
from pythongame.core.projectile_controllers import create_projectile_controller, register_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualCircle, VisualRect
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy

PROJECTILE_TYPE = ProjectileType.ENEMY_SKELETON_BOSS
PROJECTILE_SIZE = (20, 20)
BUFF_STUNNED = BuffType.ENEMY_SKELETON_BOSS_STUNNED_FROM_FIRING


class State(Enum):
    BASE = 1
    FIRING = 2


class NpcMind(MeleeEnemyNpcMind):
    STATE_DURATION_BASE = 3000
    STATE_DURATION_FIRING = 1200
    FIRE_COOLDOWN = 350

    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 6, 0, Millis(900))
        self._time_since_state_change = 0
        self._state = State.BASE
        self._time_since_fired = 0

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return
        super().control_npc(game_state, npc, player_entity, is_player_invisible, time_passed)

        self._time_since_state_change += time_passed

        if self._state == State.BASE:
            if self._time_since_state_change > NpcMind.STATE_DURATION_BASE:
                self._time_since_state_change -= NpcMind.STATE_DURATION_BASE
                self._state = State.FIRING

                npc.gain_buff_effect(get_buff_effect(BUFF_STUNNED),
                                     Millis(NpcMind.STATE_DURATION_FIRING))
                return
        elif self._state == State.FIRING:
            if self._time_since_state_change > NpcMind.STATE_DURATION_FIRING:
                self._time_since_state_change -= NpcMind.STATE_DURATION_FIRING
                self._state = State.BASE
                return
            self._time_since_fired += time_passed
            if self._time_since_fired > NpcMind.FIRE_COOLDOWN:
                self._time_since_fired -= NpcMind.FIRE_COOLDOWN
                directions_to_player = get_directions_to_position(npc.world_entity, player_entity.get_position())
                new_direction = directions_to_player[0]
                if random.random() < 0.1 and directions_to_player[1] is not None:
                    new_direction = directions_to_player[1]
                npc.world_entity.direction = new_direction
                npc.world_entity.set_not_moving()
                center_position = npc.world_entity.get_center_position()
                distance_from_enemy = 35
                projectile_pos = translate_in_direction(
                    get_position_from_center_position(center_position, PROJECTILE_SIZE),
                    npc.world_entity.direction, distance_from_enemy)
                projectile_speed = 0.3
                projectile_entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, Sprite.NONE,
                                                npc.world_entity.direction, projectile_speed)
                projectile = Projectile(projectile_entity, create_projectile_controller(PROJECTILE_TYPE))
                game_state.game_world.projectile_entities.append(projectile)
                play_sound(SoundId.ENEMY_MAGIC_SKELETON_BOSS)


class StunnedFromFiring(StunningBuffEffect):
    def __init__(self):
        super().__init__(BUFF_STUNNED)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)
        self._color = (180, 180, 50)
        self._timer = PeriodicTimer(Millis(100))
        self._min_damage = 4
        self._max_damage = 6

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        if self._timer.update_and_check_if_ready(time_passed):
            color = (random.randint(150, 200), random.randint(150, 200), random.randint(50, 100))
            head = VisualRect(color, projectile.world_entity.get_center_position(), 15, 15,
                              Millis(120), 4, projectile.world_entity)
            tail = VisualCircle(color, projectile.world_entity.get_center_position(), 13, 13,
                                Millis(180), 2)
            game_state.game_world.visual_effects += [head, tail]

    def apply_player_collision(self, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_damage_to_player(game_state, damage, DamageType.MAGIC, None)
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, game_state.game_world.player_entity.get_center_position(),
                         25, 35, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_player_summon_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_npc_damage_to_npc(game_state, npc, damage)
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, npc.world_entity.get_center_position(), 25, 35, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, projectile.world_entity.get_center_position(), 13, 26, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True


def register_skeleton_boss_enemy():
    x = 6
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x + i, y + 0) for i in range(3)],
        Direction.LEFT: [(x + i, y + 1) for i in range(3)],
        Direction.RIGHT: [(x + i, y + 2) for i in range(3)],
        Direction.UP: [(x + i, y + 3) for i in range(3)]
    }

    register_basic_enemy(
        npc_type=NpcType.SKELETON_BOSS,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_SKELETON_BOSS,
            size=(32, 32),
            max_health=120,
            health_regen=3,
            speed=0.07,
            exp_reward=60,
            enemy_loot_table=LootTableId.BOSS_SKELETON,
            death_sound_id=SoundId.DEATH_BOSS,
            is_boss=True),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(52, 56),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-10, -24)
    )

    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
    register_buff_effect(BUFF_STUNNED, StunnedFromFiring)
