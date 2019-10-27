from pythongame.core.common import Direction
from pythongame.core.game_data import register_entity_sprite_map, Sprite
from pythongame.core.view.image_loading import SpriteSheet


def register_decorations():
    _register_ground_decorations()
    _register_plant_decoration()


def _register_ground_decorations():
    sprite_sheet = SpriteSheet("resources/graphics/material_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(4, 4)]}
    register_entity_sprite_map(Sprite.DECORATION_GROUND_STONE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
    register_entity_sprite_map(Sprite.DECORATION_GROUND_STONE_GRAY, sprite_sheet, original_sprite_size,
                               scaled_sprite_size, {Direction.DOWN: [(0, 2)]}, (0, 0))


def _register_plant_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(12, 1)]}
    register_entity_sprite_map(Sprite.DECORATION_PLANT, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
