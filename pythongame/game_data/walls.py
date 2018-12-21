from pythongame.core.common import WallType, Sprite, Direction
from pythongame.core.game_data import register_wall_data, WallData, register_entity_sprite_map, SpriteSheet


def register_walls():
    _register_wall()
    _register_statue()


def _register_wall():
    size = (25, 25)
    sprite = Sprite.WALL
    sprite_sheet = SpriteSheet("resources/graphics/stone_tile.png")
    original_sprite_size = (410, 404)
    scaled_sprite_size = (size[0] - 1, size[1] - 1)
    indices_by_dir = {
        Direction.DOWN: [(0, 0)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (1, 1))
    register_wall_data(WallType.WALL, WallData(sprite, size))


def _register_statue():
    sprite = Sprite.WALL_STATUE
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    indices_by_dir = {Direction.DOWN: [(13, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-4, -54))
    register_wall_data(WallType.STATUE, WallData(sprite, (42, 46)))
