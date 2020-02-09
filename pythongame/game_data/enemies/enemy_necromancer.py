import random

from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, ProjectileType, PeriodicTimer, \
    LootTableId
from pythongame.core.damage_interactions import deal_damage_to_player, DamageType, deal_npc_damage_to_npc
from pythongame.core.entity_creation import create_npc
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    NON_PLAYER_CHARACTERS
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, Projectile
from pythongame.core.math import random_direction, get_position_from_center_position, sum_of_vectors, \
    is_x_and_y_within_distance, rect_from_corners, get_directions_to_position, translate_in_direction
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import AbstractProjectileController, register_projectile_controller, \
    create_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualLine, VisualCircle

SPRITE = Sprite.ENEMY_NECROMANCER
ENEMY_TYPE = NpcType.NECROMANCER
PROJECTILE_TYPE = ProjectileType.ENEMY_NECROMANCER
PROJECTILE_SIZE = (30, 30)


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_summoning = 0
        self._summoning_cooldown = self._random_summoning_cooldown()
        self._time_since_healing = 0
        self._healing_cooldown = self._random_healing_cooldown()
        self._alive_summons = []
        self._time_since_shoot = 0
        self._shoot_cooldown = self._random_shoot_cooldown()

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_summoning += time_passed
        self._time_since_healing += time_passed
        self._time_since_shoot += time_passed
        if self._time_since_summoning > self._summoning_cooldown:
            necro_center_pos = npc.world_entity.get_center_position()
            self._time_since_summoning = 0
            self._alive_summons = [summon for summon in self._alive_summons
                                   if summon in game_state.non_player_characters]
            if len(self._alive_summons) < 3:
                relative_pos_from_summoner = (random.randint(-150, 150), random.randint(-150, 150))
                summon_center_pos = sum_of_vectors(necro_center_pos, relative_pos_from_summoner)
                summon_type = random.choice([NpcType.ZOMBIE, NpcType.MUMMY])
                summon_size = NON_PLAYER_CHARACTERS[summon_type].size
                summon_pos = game_state.get_within_world(
                    get_position_from_center_position(summon_center_pos, summon_size), summon_size)
                summon_enemy = create_npc(summon_type, summon_pos)
                is_wall_blocking = game_state.walls_state.does_rect_intersect_with_wall(
                    rect_from_corners(necro_center_pos, summon_center_pos))
                is_position_blocked = game_state.would_entity_collide_if_new_pos(summon_enemy.world_entity, summon_pos)
                if not is_wall_blocking and not is_position_blocked:
                    self._summoning_cooldown = self._random_summoning_cooldown()
                    game_state.add_non_player_character(summon_enemy)
                    self._alive_summons.append(summon_enemy)
                    game_state.visual_effects.append(
                        VisualCircle((80, 150, 100), necro_center_pos, 40, 70, Millis(120), 3))
                    game_state.visual_effects.append(
                        VisualCircle((80, 150, 100), summon_center_pos, 40, 70, Millis(120), 3))
                    play_sound(SoundId.ENEMY_NECROMANCER_SUMMON)
                else:
                    # Failed to summon, so try again without waiting full duration
                    self._summoning_cooldown = 500
            else:
                self._summoning_cooldown = self._random_summoning_cooldown()

        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            self._healing_cooldown = self._random_healing_cooldown()
            necro_center_pos = npc.world_entity.get_center_position()
            nearby_hurt_enemies = [
                e for e in game_state.non_player_characters
                if e.is_enemy
                   and is_x_and_y_within_distance(necro_center_pos, e.world_entity.get_center_position(), 200)
                   and e != npc and not e.health_resource.is_at_max()
            ]
            if nearby_hurt_enemies:
                healing_target = nearby_hurt_enemies[0]
                healing_target.health_resource.gain(5)
                healing_target_pos = healing_target.world_entity.get_center_position()
                visual_line = VisualLine((80, 200, 150), necro_center_pos, healing_target_pos, Millis(350), 3)
                game_state.visual_effects.append(visual_line)
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
            game_state.projectile_entities.append(projectile)
            play_sound(SoundId.ENEMY_ATTACK_NECRO)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                npc.world_entity.set_moving_in_dir(direction)
            else:
                npc.world_entity.set_not_moving()

    @staticmethod
    def _random_summoning_cooldown():
        return random.randint(500, 5500)

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
            game_state.visual_effects += [head, tail]

    def apply_player_collision(self, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_damage_to_player(game_state, damage, DamageType.MAGIC, None)
        game_state.visual_effects.append(VisualCircle(self._color, game_state.player_entity.get_center_position(),
                                                      25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_player_summon_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_npc_damage_to_npc(game_state, npc, damage)
        game_state.visual_effects.append(
            VisualCircle(self._color, npc.world_entity.get_center_position(), 25, 50, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        game_state.visual_effects.append(
            VisualCircle(self._color, projectile.world_entity.get_center_position(), 13, 26, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True


def register_necromancer_enemy():
    size = (36, 36)
    health = 60
    exp_reward = 29
    npc_data = NpcData.enemy(SPRITE, size, health, 0, 0.02, exp_reward, LootTableId.LEVEL_4, SoundId.DEATH_NECRO)
    register_npc_data(ENEMY_TYPE, npc_data)
    register_npc_behavior(ENEMY_TYPE, NpcMind)

    enemy_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    enemy_original_sprite_size = (32, 32)
    enemy_scaled_sprite_size = (48, 64)
    enemy_indices_by_dir = {
        Direction.DOWN: [(x, 0) for x in range(9, 12)],
        Direction.LEFT: [(x, 1) for x in range(9, 12)],
        Direction.RIGHT: [(x, 2) for x in range(9, 12)],
        Direction.UP: [(x, 3) for x in range(9, 12)]
    }
    register_entity_sprite_map(SPRITE, enemy_sprite_sheet, enemy_original_sprite_size,
                               enemy_scaled_sprite_size, enemy_indices_by_dir, (-6, -28))
    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
