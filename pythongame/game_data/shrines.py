from pythongame.core.common import Direction
from pythongame.core.game_data import Sprite, register_entity_sprite_map
from pythongame.core.view.image_loading import SpriteSheet

SHRINE_ENTITY_SIZE = (42, 39)


def register_shrines():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    register_entity_sprite_map(Sprite.SHRINE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               {Direction.DOWN: [(14, 3)]}, (-7, -54))
