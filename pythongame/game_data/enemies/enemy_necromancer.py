import random

from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, ProjectileType, PeriodicTimer, \
    LootTableId
from pythongame.core.damage_interactions import deal_damage_to_player, DamageType, deal_npc_damage_to_npc
from pythongame.core.entity_creation import create_npc
from pythongame.core.game_data import NpcData
from pythongame.core.game_state import GameState, NonPlayerCharacter, Projectile
from pythongame.core.math import get_position_from_center_position, is_x_and_y_within_distance, \
    get_directions_to_position, translate_in_direction
from pythongame.core.npc_behaviors import AbstractNpcMind, EnemySummonTrait, EnemyRandomWalkTrait
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import AbstractProjectileController, register_projectile_controller, \
    create_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualLine, VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy

PROJECTILE_TYPE = ProjectileType.ENEMY_NECROMANCER
PROJECTILE_SIZE = (30, 30)


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._time_since_healing = 0
        self._healing_cooldown = self._random_healing_cooldown()
        self._time_since_shoot = 0
        self._shoot_cooldown = self._random_shoot_cooldown()
        self._summon_trait = EnemySummonTrait(3, [NpcType.ZOMBIE, NpcType.MUMMY], (Millis(500), Millis(5500)),
                                              create_npc)
        self._random_walk_trait = EnemyRandomWalkTrait(Millis(750))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return

        self._summon_trait.update(npc, game_state, time_passed)
        self._random_walk_trait.update(npc, game_state, time_passed)

        self._time_since_healing += time_passed
        self._time_since_shoot += time_passed

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            self._healing_cooldown = self._random_healing_cooldown()
            necro_center_pos = npc.world_entity.get_center_position()
            nearby_hurt_enemies = [
                e for e in game_state.game_world.non_player_characters
                if e.is_enemy
                   and is_x_and_y_within_distance(necro_center_pos, e.world_entity.get_center_position(), 200)
                   and e != npc and not e.health_resource.is_at_max()
            ]
            if nearby_hurt_enemies:
                healing_target = nearby_hurt_enemies[0]
                healing_target.health_resource.gain(5)
                healing_target_pos = healing_target.world_entity.get_center_position()
                visual_line = VisualLine((80, 200, 150), necro_center_pos, healing_target_pos, Millis(350), 3)
                game_state.game_world.visual_effects.append(visual_line)
                play_sound(SoundId.ENEMY_NECROMANCER_HEAL)

        if self._time_since_shoot > self._shoot_cooldown:
            self._time_since_shoot = 0
            self._shoot_cooldown = self._random_shoot_cooldown()
            npc.world_entity.direction = get_directions_to_position(npc.world_entity, player_entity.get_position())[0]
            npc.world_entity.set_not_moving()
            center_position = npc.world_entity.get_center_position()
            distance_from_enemy = 35
            projectile_pos = translate_in_direction(
                get_position_from_center_position(center_position, PROJECTILE_SIZE),
                npc.world_entity.direction, distance_from_enemy)
            projectile_speed = 0.2
            projectile_entity = WorldEntity(projectile_pos, PROJECTILE_SIZE, Sprite.NONE, npc.world_entity.direction,
                                            projectile_speed)
            projectile = Projectile(projectile_entity, create_projectile_controller(PROJECTILE_TYPE))
            game_state.game_world.projectile_entities.append(projectile)
            play_sound(SoundId.ENEMY_ATTACK_NECRO)

    @staticmethod
    def _random_healing_cooldown():
        return random.randint(1000, 9000)

    @staticmethod
    def _random_shoot_cooldown():
        return random.randint(2000, 10_000)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)
        self._color = (50, 180, 50)
        self._timer = PeriodicTimer(Millis(100))
        self._min_damage = 8
        self._max_damage = 12

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        if self._timer.update_and_check_if_ready(time_passed):
            head = VisualCircle(self._color, projectile.world_entity.get_center_position(), 15, 15,
                                Millis(150), 0, projectile.world_entity)
            tail = VisualCircle(self._color, projectile.world_entity.get_center_position(), 15, 1,
                                Millis(400), 0)
            game_state.game_world.visual_effects += [head, tail]

    def apply_player_collision(self, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_damage_to_player(game_state, damage, DamageType.MAGIC, None)
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, game_state.game_world.player_entity.get_center_position(),
                         25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_player_summon_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_npc_damage_to_npc(game_state, npc, damage)
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, npc.world_entity.get_center_position(), 25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        game_state.game_world.visual_effects.append(
            VisualCircle(self._color, projectile.world_entity.get_center_position(), 13, 26, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True


def register_necromancer_enemy():
    indices_by_dir = {
        Direction.DOWN: [(x, 0) for x in range(9, 12)],
        Direction.LEFT: [(x, 1) for x in range(9, 12)],
        Direction.RIGHT: [(x, 2) for x in range(9, 12)],
        Direction.UP: [(x, 3) for x in range(9, 12)]
    }

    register_basic_enemy(
        npc_type=NpcType.NECROMANCER,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_NECROMANCER,
            size=(36, 36),
            max_health=60,
            health_regen=0,
            speed=0.02,
            exp_reward=29,
            enemy_loot_table=LootTableId.LEVEL_5,
            death_sound_id=SoundId.DEATH_NECRO),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_3.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 64),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-6, -28)
    )

    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
