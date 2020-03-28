from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 5, 0.1, Millis(900))


def register_zombie_fast_enemy():
    x = 6
    y = 4
    indices_by_dir = {
        Direction.DOWN: [(x, y), (x + 1, y), (x + 2, y)],
        Direction.LEFT: [(x, y + 1), (x + 1, y + 1), (x + 2, y + 1)],
        Direction.RIGHT: [(x, y + 2), (x + 1, y + 2), (x + 2, y + 2)],
        Direction.UP: [(x, y + 3), (x + 1, y + 3), (x + 2, y + 3)]
    }

    register_basic_enemy(
        npc_type=NpcType.ZOMBIE_FAST,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_ZOMBIE_FAST,
            size=(30, 30),
            max_health=20,
            health_regen=0,
            speed=0.11,
            exp_reward=15,
            enemy_loot_table=LootTableId.LEVEL_4,
            death_sound_id=SoundId.DEATH_ZOMBIE),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-9, -18)
    )
