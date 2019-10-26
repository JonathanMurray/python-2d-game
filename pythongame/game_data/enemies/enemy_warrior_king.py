from pythongame.core.common import Millis, NpcType, Sprite, Direction, ConsumableType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map
from pythongame.core.image_loading import SpriteSheet
from pythongame.core.loot import LootTable, LootGroup, LootEntry
from pythongame.core.npc_behaviors import register_npc_behavior, MeleeEnemyNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.loot_tables import LOOT_ITEMS_4, LOOT_ITEMS_3, LOOT_ITEMS_2


class NpcMind(MeleeEnemyNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder, Millis(2000), 17, 0, Millis(600))


def register_warrior_king_enemy():
    size = (32, 32)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.ENEMY_WARRIOR_KING
    npc_type = NpcType.WARRIOR_KING
    movement_speed = 0.13
    health = 190
    exp_reward = 75
    loot_table = LootTable(
        [
            LootGroup.single(LootEntry.consumable(ConsumableType.WARP_STONE), 1),
            LootGroup(1, LOOT_ITEMS_4, 1),
            LootGroup(1, LOOT_ITEMS_2 + LOOT_ITEMS_3 + LOOT_ITEMS_4, 0.7),
            LootGroup(1, [LootEntry.money(3), LootEntry.money(5), LootEntry.money(7)], 0.7)
        ]
    )
    npc_data = NpcData.enemy(sprite, size, health, 0, movement_speed, exp_reward, loot_table)
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
