from pythongame.core.common import NpcType, Sprite, Direction, Millis, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 6, 0, Millis(900))


def register_skeleton_boss_enemy():
    x = 6
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x + i, y + 0) for i in range(3)],
        Direction.LEFT: [(x + i, y + 1) for i in range(3)],
        Direction.RIGHT: [(x + i, y + 2) for i in range(3)],
        Direction.UP: [(x + i, y + 3) for i in range(3)]
    }

    register_basic_enemy(
        npc_type=NpcType.SKELETON_BOSS,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_SKELETON_BOSS,
            size=(32, 32),
            max_health=120,
            health_regen=2,
            speed=0.06,
            exp_reward=60,
            enemy_loot_table=LootTableId.BOSS_SKELETON,
            death_sound_id=SoundId.DEATH_BOSS,
            is_boss=True),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(52, 56),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-10, -24)
    )
