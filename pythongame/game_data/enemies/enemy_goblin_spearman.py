import random

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import NpcType, Sprite, Direction, Millis, BuffType, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.math import get_manhattan_distance
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy

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
        if npc.stun_status.is_stunned():
            return
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
    x = 9
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x + i, y + 0) for i in range(3)],
        Direction.LEFT: [(x + i, y + 1) for i in range(3)],
        Direction.RIGHT: [(x + i, y + 2) for i in range(3)],
        Direction.UP: [(x + i, y + 3) for i in range(3)]
    }

    register_basic_enemy(
        npc_type=NpcType.GOBLIN_SPEARMAN,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_GOBLIN_SPEARMAN,
            size=(24, 24),
            max_health=21,
            health_regen=0,
            speed=0.08,
            exp_reward=14,
            enemy_loot_table=LootTableId.LEVEL_3,
            death_sound_id=SoundId.DEATH_GOBLIN),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_2.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-12, -24)
    )
