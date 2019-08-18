from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.loot_tables import LOOT_TABLE_2


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 3, 0.1, Millis(900))


def register_zombie_enemy():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_ZOMBIE
    npc_type = NpcType.ZOMBIE
    movement_speed = 0.03
    health = 15
    exp_reward = 10
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LOOT_TABLE_2,
                             SoundId.DEATH_ZOMBIE)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-9, -18))
