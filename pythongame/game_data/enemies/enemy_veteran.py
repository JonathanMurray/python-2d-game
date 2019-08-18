from pythongame.core.common import NpcType, Sprite, Direction, Millis
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.loot_tables import LOOT_TABLE_4


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 13, 0, Millis(600))


def register_veteran_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_VETERAN
    npc_type = NpcType.VETERAN
    movement_speed = 0.08
    health = 60
    exp_reward = 35
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LOOT_TABLE_4)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_veteran.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)

    sheet_x = 0
    indices_by_dir = {
        Direction.DOWN: [(sheet_x, 0), (sheet_x + 1, 0), (sheet_x + 2, 0), (sheet_x + 1, 0)],
        Direction.LEFT: [(sheet_x, 1), (sheet_x + 1, 1), (sheet_x + 2, 1), (sheet_x + 1, 1)],
        Direction.RIGHT: [(sheet_x, 2), (sheet_x + 1, 2), (sheet_x + 2, 2), (sheet_x + 1, 2)],
        Direction.UP: [(sheet_x, 3), (sheet_x + 1, 3), (sheet_x + 2, 3), (sheet_x + 1, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
