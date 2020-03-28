from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1500), 12, 0, Millis(900))


def register_goblin_warrior_enemy():
    x = 3
    y = 4
    indices_by_dir = {
        Direction.DOWN: [(x + i, y + 0) for i in range(3)],
        Direction.LEFT: [(x + i, y + 1) for i in range(3)],
        Direction.RIGHT: [(x + i, y + 2) for i in range(3)],
        Direction.UP: [(x + i, y + 3) for i in range(3)]
    }

    register_basic_enemy(
        npc_type=NpcType.GOBLIN_WARRIOR,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_GOBLIN_WARRIOR,
            size=(32, 32),
            max_health=110,
            health_regen=0,
            speed=0.09,
            exp_reward=50,
            enemy_loot_table=LootTableId.BOSS_GOBLIN,
            death_sound_id=SoundId.DEATH_BOSS,
            is_boss=True),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/enemy_sprite_sheet_2.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(52, 52),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-10, -20)
    )
