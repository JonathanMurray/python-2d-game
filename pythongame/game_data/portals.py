from pythongame.core.common import Direction
from pythongame.core.game_data import SpriteSheet, Sprite, register_entity_sprite_map

PORTAL_SIZE = (38, 40)

def register_portal():
    sprite = Sprite.PORTAL
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    indices_by_dir = {Direction.DOWN: [(14, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-8, -52))
