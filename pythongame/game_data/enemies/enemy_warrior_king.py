from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 24, 0, Millis(600))


def register_warrior_king_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_WARRIOR_KING
    npc_type = NpcType.WARRIOR_KING
    movement_speed = 0.13
    health = 240
    exp_reward = 75

    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LootTableId.BOSS_WARRIOR_KING,
                             SoundId.DEATH_BOSS, is_boss=True)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (54, 60)
    x = 9
    indices_by_dir = {
        Direction.DOWN: [(x, 4), (x + 1, 4), (x + 2, 4)],
        Direction.LEFT: [(x, 5), (x + 1, 5), (x + 2, 5)],
        Direction.RIGHT: [(x, 6), (x + 1, 6), (x + 2, 6)],
        Direction.UP: [(x, 7), (x + 1, 7), (x + 2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-11, -23))
