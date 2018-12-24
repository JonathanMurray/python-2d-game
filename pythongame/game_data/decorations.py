from pythongame.core.common import Direction
from pythongame.core.game_data import register_entity_sprite_map, Sprite, SpriteSheet


def register_decorations():
    _register_ground_decoration()
    _register_plant_decoration()
    _register_engangling_roots_effect_decoration()


def _register_ground_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/material_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    # good looking floor tiles: 2,2     2,4     4,4     0,2
    indices_by_dir = {Direction.DOWN: [(4, 4)]}
    register_entity_sprite_map(Sprite.DECORATION_GROUND_STONE, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))


def _register_engangling_roots_effect_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/entangling_roots.png")
    original_sprite_size = (130, 114)
    scaled_sprite_size = (50, 50)
    # good looking floor tiles: 2,2     2,4     4,4     0,2
    indices_by_dir = {Direction.DOWN: [(0, 0)]}
    register_entity_sprite_map(Sprite.DECORATION_ENTANGLING_ROOTS_EFFECT, sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, (0, 0))


def _register_plant_decoration():
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(12, 1)]}
    register_entity_sprite_map(Sprite.DECORATION_PLANT, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
