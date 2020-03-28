from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 24, 0, Millis(600))


def register_warrior_king_enemy():
    x = 9
    indices_by_dir = {
        Direction.DOWN: [(x, 4), (x + 1, 4), (x + 2, 4)],
        Direction.LEFT: [(x, 5), (x + 1, 5), (x + 2, 5)],
        Direction.RIGHT: [(x, 6), (x + 1, 6), (x + 2, 6)],
        Direction.UP: [(x, 7), (x + 1, 7), (x + 2, 7)]
    }

    register_basic_enemy(
        npc_type=NpcType.WARRIOR_KING,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_WARRIOR_KING,
            size=(32, 32),
            max_health=240,
            health_regen=0,
            speed=0.13,
            exp_reward=90,
            enemy_loot_table=LootTableId.BOSS_WARRIOR_KING,
            death_sound_id=SoundId.DEATH_BOSS,
            is_boss=True),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_3.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(54, 60),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-11, -23),
    )
