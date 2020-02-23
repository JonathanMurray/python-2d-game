from pythongame.core.common import NpcType, Sprite, Direction, Millis, SoundId, LootTableId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 8, 0, Millis(600))


def register_warrior_enemy():
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x, 0), (x + 1, 0), (x + 2, 0), (x + 1, 0)],
        Direction.LEFT: [(x, 1), (x + 1, 1), (x + 2, 1), (x + 1, 1)],
        Direction.RIGHT: [(x, 2), (x + 1, 2), (x + 2, 2), (x + 1, 2)],
        Direction.UP: [(x, 3), (x + 1, 3), (x + 2, 3), (x + 1, 3)]
    }

    register_basic_enemy(
        npc_type=NpcType.WARRIOR,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_WARRIOR,
            size=(32, 32),
            max_health=32,
            health_regen=0,
            speed=0.12,
            exp_reward=25,
            enemy_loot_table=LootTableId.LEVEL_5,
            death_sound_id=SoundId.DEATH_HUMAN),
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/human_spritesheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-8, -16)
    )
