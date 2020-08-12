import random
from typing import Tuple

from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, PeriodicTimer, \
    LootTableId, ProjectileType
from pythongame.core.damage_interactions import deal_damage_to_player, DamageType, deal_npc_damage_to_npc
from pythongame.core.game_data import NpcData
from pythongame.core.game_state import GameState, NonPlayerCharacter, Projectile
from pythongame.core.npc_behaviors import AbstractNpcMind, EnemyShootProjectileTrait, EnemyRandomWalkTrait
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import AbstractProjectileController, create_projectile_controller, \
    register_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import VisualCircle, VisualRect, create_visual_healing_text
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy

PROJECTILE_TYPE = ProjectileType.ENEMY_SKELETON_MAGE
PROJECTILE_SIZE = (13, 13)


def create_projectile(pos: Tuple[int, int], direction: Direction):
    world_entity = WorldEntity(pos, PROJECTILE_SIZE, Sprite.NONE, direction, 0.2)
    return Projectile(world_entity, create_projectile_controller(PROJECTILE_TYPE))


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._random_walk_trait = EnemyRandomWalkTrait(Millis(750))
        self._time_since_healing = 0
        self._healing_cooldown = self._random_healing_cooldown()
        self._shoot_fireball_trait = EnemyShootProjectileTrait(
            create_projectile=create_projectile,
            projectile_size=PROJECTILE_SIZE,
            cooldown_interval=(Millis(1000), Millis(4000)),
            chance_to_shoot_other_direction=0,
            sound_id=SoundId.ENEMY_ATTACK_SKELETON_MAGE)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        if npc.stun_status.is_stunned():
            return
        self._time_since_healing += time_passed
        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            self._healing_cooldown = self._random_healing_cooldown()
            if not npc.health_resource.is_at_max():
                healing_amount = random.randint(10, 20)
                npc.health_resource.gain(healing_amount)
                circle_effect = VisualCircle((80, 200, 150), npc.world_entity.get_center_position(), 30, 50,
                                             Millis(350), 3)
                game_state.game_world.visual_effects.append(circle_effect)
                number_effect = create_visual_healing_text(npc.world_entity, healing_amount)
                game_state.game_world.visual_effects.append(number_effect)
                play_sound(SoundId.ENEMY_SKELETON_MAGE_HEAL)

        self._shoot_fireball_trait.update(npc, game_state, time_passed)
        self._random_walk_trait.update(npc, game_state, time_passed)

    @staticmethod
    def _random_healing_cooldown():
        return random.randint(4000, 9000)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)
        self._color = (180, 180, 50)
        self._timer = PeriodicTimer(Millis(100))
        self._min_damage = 3
        self._max_damage = 6

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        if self._timer.update_and_check_if_ready(time_passed):
            color = (random.randint(150, 200), random.randint(150, 200), random.randint(50, 100))
            head = VisualRect(color, projectile.world_entity.get_center_position(), 15, 15,
                              Millis(150), 4, projectile.world_entity)
            tail = VisualCircle(color, projectile.world_entity.get_center_position(), 13, 13,
                                Millis(400), 2)
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


def register_skeleton_mage_enemy():
    x = 3
    indices_by_dir = {
        Direction.DOWN: [(x, 0), (x + 1, 0), (x + 2, 0), (x + 1, 0)],
        Direction.LEFT: [(x, 1), (x + 1, 1), (x + 2, 1), (x + 1, 1)],
        Direction.RIGHT: [(x, 2), (x + 1, 2), (x + 2, 2), (x + 1, 2)],
        Direction.UP: [(x, 3), (x + 1, 3), (x + 2, 3), (x + 1, 3)]
    }
    register_basic_enemy(
        npc_type=NpcType.SKELETON_MAGE,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_SKELETON_MAGE,
            size=(32, 32),
            max_health=50,
            health_regen=0,
            speed=0.05,
            exp_reward=25,
            enemy_loot_table=LootTableId.LEVEL_4,
            death_sound_id=SoundId.DEATH_SKELETON_MAGE),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/monsters_spritesheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-8, -16)
    )

    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
