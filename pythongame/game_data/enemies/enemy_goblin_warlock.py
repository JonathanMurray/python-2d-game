import random
from typing import Tuple

from pythongame.core.buff_effects import get_buff_effect, AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Millis, NpcType, Sprite, \
    ProjectileType, BuffType, Direction, SoundId, LootTableId
from pythongame.core.damage_interactions import deal_damage_to_player, deal_npc_damage_to_npc, DamageType
from pythongame.core.enemy_target_selection import EnemyTarget, get_target
from pythongame.core.game_data import NpcData, register_buff_text, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, Projectile
from pythongame.core.math import get_perpendicular_directions
from pythongame.core.npc_behaviors import AbstractNpcMind, EnemyShootProjectileTrait
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.pathfinding.npc_pathfinding import NpcPathfinder
from pythongame.core.projectile_controllers import create_projectile_controller, AbstractProjectileController, \
    register_projectile_controller
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy

BUFF_TYPE = BuffType.ENEMY_GOBLIN_WARLOCK_BURNT
PROJECTILE_TYPE = ProjectileType.ENEMY_GOBLIN_WARLOCK
PROJECTILE_SPRITE = Sprite.PROJECTILE_ENEMY_GOBLIN_WARLOCK
PROJECTILE_SIZE = (20, 20)


def create_projectile(pos: Tuple[int, int], direction: Direction):
    world_entity = WorldEntity(pos, PROJECTILE_SIZE, PROJECTILE_SPRITE, direction, 0.11)
    return Projectile(world_entity, create_projectile_controller(PROJECTILE_TYPE))


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 900
        self._time_since_updated_path = random.randint(0, self._update_path_interval)
        self.pathfinder = NpcPathfinder(global_path_finder)
        self.next_waypoint = None
        self._reevaluate_next_waypoint_direction_interval = 1000
        self._time_since_reevaluated = self._reevaluate_next_waypoint_direction_interval
        self._shoot_fireball_trait = EnemyShootProjectileTrait(
            create_projectile=create_projectile,
            projectile_size=PROJECTILE_SIZE,
            cooldown_interval=(Millis(500), Millis(5000)),
            chance_to_shoot_other_direction=0.3,
            sound_id=SoundId.ENEMY_ATTACK_GOBLIN_WARLOCK)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return
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
                if random.random() < 0.5 and direction:
                    direction = random.choice(get_perpendicular_directions(direction))
                _move_in_dir(enemy_entity, direction)
            else:
                enemy_entity.set_not_moving()

        self._shoot_fireball_trait.update(npc, game_state, time_passed)


def _move_in_dir(enemy_entity, direction):
    if direction:
        enemy_entity.set_moving_in_dir(direction)
    else:
        enemy_entity.set_not_moving()


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState, projectile: Projectile):
        deal_damage_to_player(game_state, 1, DamageType.MAGIC, None)
        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.ENEMY_GOBLIN_WARLOCK_BURNT), Millis(5000))
        game_state.game_world.visual_effects.append(
            VisualCircle((180, 50, 50), game_state.game_world.player_entity.get_center_position(),
                         25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_player_summon_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        deal_npc_damage_to_npc(game_state, npc, 1)
        npc.gain_buff_effect(get_buff_effect(BuffType.ENEMY_GOBLIN_WARLOCK_BURNT), Millis(5000))
        game_state.game_world.visual_effects.append(
            VisualCircle((180, 50, 50), npc.world_entity.get_center_position(), 25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        game_state.game_world.visual_effects.append(
            VisualCircle((180, 50, 50), projectile.world_entity.get_center_position(), 12, 24, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True


class Burnt(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 500:
            self._time_since_graphics = 0
            if buffed_npc:
                deal_npc_damage_to_npc(game_state, buffed_npc, 2)
                game_state.game_world.visual_effects.append(
                    VisualCircle((180, 50, 50), buffed_npc.world_entity.get_center_position(), 10, 20, Millis(50), 0,
                                 buffed_entity))
            else:
                deal_damage_to_player(game_state, 2, DamageType.MAGIC, None)
                game_state.game_world.visual_effects.append(
                    VisualCircle((180, 50, 50), game_state.game_world.player_entity.get_center_position(), 10, 20,
                                 Millis(50), 0,
                                 buffed_entity))

    def get_buff_type(self):
        return BUFF_TYPE


def register_goblin_warlock_enemy():
    enemy_indices_by_dir = {
        Direction.DOWN: [(0, 4), (1, 4), (2, 4)],
        Direction.LEFT: [(0, 5), (1, 5), (2, 5)],
        Direction.RIGHT: [(0, 6), (1, 6), (2, 6)],
        Direction.UP: [(0, 7), (1, 7), (2, 7)]
    }
    register_basic_enemy(
        npc_type=NpcType.GOBLIN_WARLOCK,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_GOBLIN_WARLOCK,
            size=(24, 24),
            max_health=21,
            health_regen=0,
            speed=0.032,
            exp_reward=14,
            enemy_loot_table=LootTableId.LEVEL_4,
            death_sound_id=SoundId.DEATH_GOBLIN),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_2.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=enemy_indices_by_dir,
        sprite_position_relative_to_entity=(-12, -24)
    )

    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)

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
