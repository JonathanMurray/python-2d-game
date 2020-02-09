from pythongame.core.common import Millis, NpcType, Sprite, Direction, SoundId, LootTableId
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(1500), 12, 0, Millis(900))


def register_goblin_warrior_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_GOBLIN_WARRIOR
    npc_type = NpcType.GOBLIN_WARRIOR
    movement_speed = 0.09
    health = 110
    exp_reward = 50
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, LootTableId.BOSS_GOBLIN,
                             SoundId.DEATH_BOSS, is_boss=True)
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_2.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (52, 52)
    sprite_sheet_x = 3
    sprite_sheet_y = 4
    indices_by_dir = {
        Direction.DOWN: [(sprite_sheet_x + i, sprite_sheet_y + 0) for i in range(3)],
        Direction.LEFT: [(sprite_sheet_x + i, sprite_sheet_y + 1) for i in range(3)],
        Direction.RIGHT: [(sprite_sheet_x + i, sprite_sheet_y + 2) for i in range(3)],
        Direction.UP: [(sprite_sheet_x + i, sprite_sheet_y + 3) for i in range(3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-10, -20))
