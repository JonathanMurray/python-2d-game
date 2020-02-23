from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1500), 2, 0.1, Millis(900))


def register_rat_2_enemy():
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3)]
    }

    register_basic_enemy(
        npc_type=NpcType.RAT_2,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_RAT_2,
            size=(40, 40),
            max_health=11,
            health_regen=0,
            speed=0.08,
            exp_reward=8,
            enemy_loot_table=LootTableId.LEVEL_2,
            death_sound_id=SoundId.DEATH_RAT),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/gray_rat.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(50, 50),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-5, -5)
    )
