from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 7, 0.1, Millis(900))


def register_mummy_enemy():
    indices_by_dir = {
        Direction.DOWN: [(6, 4), (7, 4), (8, 4)],
        Direction.LEFT: [(6, 5), (7, 5), (8, 5)],
        Direction.RIGHT: [(6, 6), (7, 6), (8, 6)],
        Direction.UP: [(6, 7), (7, 7), (8, 7)]
    }

    register_basic_enemy(
        npc_type=NpcType.MUMMY,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_MUMMY,
            size=(30, 30),
            max_health=20,
            health_regen=2,
            speed=0.06,
            exp_reward=15,
            enemy_loot_table=LootTableId.LEVEL_4,
            death_sound_id=SoundId.DEATH_ZOMBIE),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_2.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-9, -18)
    )
