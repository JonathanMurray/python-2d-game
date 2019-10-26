from pythongame.core.common import NpcType, Sprite, Direction, Millis
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.loot_tables import LOOT_TABLE_2


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1000), 4, 0, Millis(900))


def register_goblin_spearman_enemy():
    size = (24, 24)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_GOBLIN_SPEARMAN
    npc_type = NpcType.GOBLIN_SPEARMAN
    movement_speed = 0.11
    health = 21
    exp_reward = 14
    register_npc_data(npc_type, NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LOOT_TABLE_2))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    sprite_sheet_x = 9
    sprite_sheet_y = 0
    indices_by_dir = {
        Direction.DOWN: [(sprite_sheet_x + i, sprite_sheet_y + 0) for i in range(3)],
        Direction.LEFT: [(sprite_sheet_x + i, sprite_sheet_y + 1) for i in range(3)],
        Direction.RIGHT: [(sprite_sheet_x + i, sprite_sheet_y + 2) for i in range(3)],
        Direction.UP: [(sprite_sheet_x + i, sprite_sheet_y + 3) for i in range(3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-12, -24))
