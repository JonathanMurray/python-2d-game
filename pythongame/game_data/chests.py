from pythongame.core.common import Sprite, Direction
from pythongame.core.game_data import SpriteSheet, register_entity_sprite_map
from pythongame.core.loot import LootTable, LootGroup
from pythongame.game_data.loot_tables import LOOT_ITEMS_1, LOOT_ITEMS_2

CHEST_ENTITY_SIZE = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
CHEST_LOOT = LootTable([LootGroup(1, LOOT_ITEMS_1 + LOOT_ITEMS_2, 1)])


def register_chest_entity():
    sprite = Sprite.CHEST
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 75)
    indices_by_dir = {Direction.DOWN: [(9, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-6, -33))
