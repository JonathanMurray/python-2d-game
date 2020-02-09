from pythongame.core.common import Sprite, Direction
from pythongame.core.game_data import register_entity_sprite_map
from pythongame.core.view.image_loading import SpriteSheet

CHEST_ENTITY_SIZE = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)


def register_chest_entity():
    sprite = Sprite.CHEST
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 75)
    indices_by_dir = {Direction.DOWN: [(9, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-6, -33))
