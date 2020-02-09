import random

from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, PeriodicTimer, \
    LootTableId, ProjectileType
from pythongame.core.damage_interactions import deal_damage_to_player, DamageType, deal_npc_damage_to_npc
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity, Projectile
from pythongame.core.math import random_direction, get_position_from_center_position, get_directions_to_position, \
    translate_in_direction
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.projectile_controllers import AbstractProjectileController, create_projectile_controller, \
    register_projectile_controller
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import VisualCircle, VisualRect, create_visual_healing_text

SPRITE = Sprite.ENEMY_SKELETON_MAGE
ENEMY_TYPE = NpcType.SKELETON_MAGE
PROJECTILE_TYPE = ProjectileType.ENEMY_SKELETON_MAGE
PROJECTILE_SIZE = (13, 13)


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._time_since_decision = 0
        self._decision_interval = 750
        self._time_since_healing = 0
        self._healing_cooldown = self._random_healing_cooldown()
        self._time_since_shoot = 0
        self._shoot_cooldown = self._random_shoot_cooldown()

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    _is_player_invisible: bool, time_passed: Millis):
        self._time_since_decision += time_passed
        self._time_since_healing += time_passed
        self._time_since_shoot += time_passed
        if self._time_since_healing > self._healing_cooldown:
            self._time_since_healing = 0
            self._healing_cooldown = self._random_healing_cooldown()
            if not npc.health_resource.is_at_max():
                healing_amount = random.randint(10, 20)
                npc.health_resource.gain(healing_amount)
                circle_effect = VisualCircle((80, 200, 150), npc.world_entity.get_center_position(), 30, 50,
                                             Millis(350), 3)
                game_state.visual_effects.append(circle_effect)
                number_effect = create_visual_healing_text(npc.world_entity, healing_amount)
                game_state.visual_effects.append(number_effect)
                play_sound(SoundId.ENEMY_SKELETON_MAGE_HEAL)

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
            play_sound(SoundId.ENEMY_ATTACK_SKELETON_MAGE)

        if self._time_since_decision > self._decision_interval:
            self._time_since_decision = 0
            if random.random() < 0.2:
                direction = random_direction()
                npc.world_entity.set_moving_in_dir(direction)
            else:
                npc.world_entity.set_not_moving()

    @staticmethod
    def _random_healing_cooldown():
        return random.randint(4000, 9000)

    @staticmethod
    def _random_shoot_cooldown():
        return random.randint(1000, 4000)


class ProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)
        self._color= (180, 180, 50)
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
            game_state.visual_effects += [head, tail]

    def apply_player_collision(self, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_damage_to_player(game_state, damage, DamageType.MAGIC, None)
        game_state.visual_effects.append(VisualCircle(self._color, game_state.player_entity.get_center_position(),
                                                      25, 35, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_player_summon_collision(self, npc: NonPlayerCharacter, game_state: GameState, projectile: Projectile):
        damage = random.randint(self._min_damage, self._max_damage)
        deal_npc_damage_to_npc(game_state, npc, damage)
        game_state.visual_effects.append(
            VisualCircle(self._color, npc.world_entity.get_center_position(), 25, 35, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True

    def apply_wall_collision(self, game_state: GameState, projectile: Projectile):
        game_state.visual_effects.append(
            VisualCircle(self._color, projectile.world_entity.get_center_position(), 13, 26, Millis(100), 0))
        projectile.has_collided_and_should_be_removed = True


def register_skeleton_mage_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_SKELETON_MAGE
    npc_type = NpcType.SKELETON_MAGE
    movement_speed = 0.05
    health = 50
    exp_reward = 25
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LootTableId.LEVEL_4,
                             SoundId.DEATH_SKELETON_MAGE)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/monsters_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)

    sheet_x = 3
    indices_by_dir = {
        Direction.DOWN: [(sheet_x, 0), (sheet_x + 1, 0), (sheet_x + 2, 0), (sheet_x + 1, 0)],
        Direction.LEFT: [(sheet_x, 1), (sheet_x + 1, 1), (sheet_x + 2, 1), (sheet_x + 1, 1)],
        Direction.RIGHT: [(sheet_x, 2), (sheet_x + 1, 2), (sheet_x + 2, 2), (sheet_x + 1, 2)],
        Direction.UP: [(sheet_x, 3), (sheet_x + 1, 3), (sheet_x + 2, 3), (sheet_x + 1, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_projectile_controller(PROJECTILE_TYPE, ProjectileController)
