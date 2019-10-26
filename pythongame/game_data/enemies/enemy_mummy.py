from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.image_loading import SpriteSheet
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.loot_tables import LOOT_TABLE_3


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 7, 0.1, Millis(900))


def register_mummy_enemy():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_MUMMY
    npc_type = NpcType.MUMMY
    movement_speed = 0.06
    health = 20
    health_regen = 2
    exp_reward = 15
    npc_data = NpcData.enemy(sprite, size, health, health_regen, movement_speed, exp_reward, LOOT_TABLE_3,
                             SoundId.DEATH_ZOMBIE)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(6, 4), (7, 4), (8, 4)],
        Direction.LEFT: [(6, 5), (7, 5), (8, 5)],
        Direction.RIGHT: [(6, 6), (7, 6), (8, 6)],
        Direction.UP: [(6, 7), (7, 7), (8, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-9, -18))
