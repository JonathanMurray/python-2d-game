from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId
from pythongame.core.game_data import NpcData
from pythongame.core.npc_behaviors import MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.enemies.register_enemies_util import register_basic_enemy
from pythongame.game_data.loot_tables import LootTableId


# TODO Make this enemy more interesting. Afflict player with burning effect on successful attack?

class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 16, 0, Millis(900))


def register_fire_demon_enemy():
    x = 0
    y = 4
    indices_by_dir = {
        Direction.DOWN: [(x, y), (x + 1, y), (x + 2, y)],
        Direction.LEFT: [(x, y + 1), (x + 1, y + 1), (x + 2, y + 1)],
        Direction.RIGHT: [(x, y + 2), (x + 1, y + 2), (x + 2, y + 2)],
        Direction.UP: [(x, y + 3), (x + 1, y + 3), (x + 2, y + 3)]
    }

    register_basic_enemy(
        npc_type=NpcType.FIRE_DEMON,
        npc_data=NpcData.enemy(
            sprite=Sprite.ENEMY_FIRE_DEMON,
            size=(32, 32),
            max_health=50,
            health_regen=0,
            speed=0.09,
            exp_reward=42,
            enemy_loot_table=LootTableId.LEVEL_5,
            death_sound_id=SoundId.DEATH_HUMAN),  # TODO
        mind_constructor=NpcMind,
        spritesheet_path="resources/graphics/monsters_spritesheet.png",
        original_sprite_size=(32, 32),
        scaled_sprite_size=(48, 48),
        spritesheet_indices=indices_by_dir,
        sprite_position_relative_to_entity=(-8, -16)
    )
