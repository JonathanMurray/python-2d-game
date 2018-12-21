from pythongame.core.common import Direction
from pythongame.core.game_data import register_entity_sprite_map, Sprite, SpriteSheet


def register_decorations():
    sprite_sheet = SpriteSheet("resources/graphics/material_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (32, 32)
    indices_by_dir = {Direction.DOWN: [(0, 2)]}
    register_entity_sprite_map(Sprite.DECORATION_GROUND_STONE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
