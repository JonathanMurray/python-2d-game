from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 2, 0.2, Millis(900))


def register_goblin_worker_enemy():
    x = 3
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x + i, y + 0) for i in range(3)],
        Direction.LEFT: [(x + i, y + 1) for i in range(3)],
        Direction.RIGHT: [(x + i, y + 2) for i in range(3)],
        Direction.UP: [(x + i, y + 3) for i in range(3)]
    }

    register_basic_enemy(
        npc_type=NpcType.GOBLIN_WORKER,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_GOBLIN_WORKER,
            size=(24, 24),
            max_health=10,
            health_regen=0,
            speed=0.07,
            exp_reward=5,
            enemy_loot_table=LootTableId.LEVEL_2,
            death_sound_id=SoundId.DEATH_GOBLIN),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_2.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-12, -24)
    )
