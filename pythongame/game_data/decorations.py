from pythongame.core.common import Direction
from pythongame.core.game_data import register_entity_sprite_map, Sprite, SpriteSheet


def register_decorations():
    _register_ground_decoration()
    _register_statue_decoration()
    _register_plant_decoration()


def _register_ground_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/material_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(0, 2)]}
    register_entity_sprite_map(Sprite.DECORATION_GROUND_STONE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))


def _register_statue_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    indices_by_dir = {Direction.DOWN: [(13, 3)]}
    register_entity_sprite_map(Sprite.DECORATION_STATUE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))


def _register_plant_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(12, 1)]}
    register_entity_sprite_map(Sprite.DECORATION_PLANT, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
