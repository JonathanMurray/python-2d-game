import random

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import NpcType, Sprite, Direction, Millis, BuffType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.math import get_manhattan_distance
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.loot_tables import LOOT_TABLE_2

SPRINT_MAX_COOLDOWN = Millis(10000)


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 4, 0, Millis(900))
        self.sprint_cooldown_remaining = self.random_cooldown()

    @staticmethod
    def random_cooldown():
        return random.randint(SPRINT_MAX_COOLDOWN // 2, SPRINT_MAX_COOLDOWN)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        super().control_npc(game_state, npc, player_entity, is_player_invisible, time_passed)
        self.sprint_cooldown_remaining -= time_passed
        sprint_distance_limit = 250
        if self.sprint_cooldown_remaining <= 0:
            is_far_away = get_manhattan_distance(
                npc.world_entity.get_position(), player_entity.get_position()) > sprint_distance_limit
            if is_far_away:
                npc.gain_buff_effect(get_buff_effect(BuffType.ENEMY_GOBLIN_SPEARMAN_SPRINT), Millis(2500))
                self.sprint_cooldown_remaining = self.random_cooldown()


def register_goblin_spearman_enemy():
    size = (24, 24)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_GOBLIN_SPEARMAN
    npc_type = NpcType.GOBLIN_SPEARMAN
    movement_speed = 0.08
    health = 21
    exp_reward = 14
    register_npc_data(npc_type, NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LOOT_TABLE_2))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    sprite_sheet_x = 9
    sprite_sheet_y = 0
    indices_by_dir = {
        Direction.DOWN: [(sprite_sheet_x + i, sprite_sheet_y + 0) for i in range(3)],
        Direction.LEFT: [(sprite_sheet_x + i, sprite_sheet_y + 1) for i in range(3)],
        Direction.RIGHT: [(sprite_sheet_x + i, sprite_sheet_y + 2) for i in range(3)],
        Direction.UP: [(sprite_sheet_x + i, sprite_sheet_y + 3) for i in range(3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-12, -24))
