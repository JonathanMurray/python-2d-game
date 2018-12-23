from pythongame.core.common import WallType, Sprite, Direction
from pythongame.core.game_data import register_wall_data, WallData, register_entity_sprite_map, SpriteSheet


def register_walls():
    _register_wall()
    _register_statue()
    _register_directional_walls()
    _register_chair()


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


def _register_directional_walls():
    _register_directional_wall(WallType.WALL_DIRECTIONAL_N, Sprite.WALL_DIRECTIONAL_N,
                               "resources/graphics/hyrule_wall_top_corner.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_NE, Sprite.WALL_DIRECTIONAL_NE,
                               "resources/graphics/hyrule_wall_top_corner.png", [1, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_E, Sprite.WALL_DIRECTIONAL_E,
                               "resources/graphics/hyrule_wall_right_corner.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_SE, Sprite.WALL_DIRECTIONAL_SE,
                               "resources/graphics/hyrule_wall_right_corner.png", [0, 1])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_S, Sprite.WALL_DIRECTIONAL_S,
                               "resources/graphics/hyrule_wall_left_corner_bot.png", [1, 1])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_SW, Sprite.WALL_DIRECTIONAL_SW,
                               "resources/graphics/hyrule_wall_left_corner_bot.png", [0, 1])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_W, Sprite.WALL_DIRECTIONAL_W,
                               "resources/graphics/hyrule_wall_left_corner_bot.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_NW, Sprite.WALL_DIRECTIONAL_NW,
                               "resources/graphics/hyrule_wall_corner.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_POINTY_NE, Sprite.WALL_DIRECTIONAL_POINTY_NE,
                               "resources/graphics/hyrule_wall_pointy_corner_ne.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_POINTY_SE, Sprite.WALL_DIRECTIONAL_POINTY_SE,
                               "resources/graphics/hyrule_wall_pointy_corner_se.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_POINTY_SW, Sprite.WALL_DIRECTIONAL_POINTY_SW,
                               "resources/graphics/hyrule_wall_pointy_corner_sw.png", [0, 0])
    _register_directional_wall(WallType.WALL_DIRECTIONAL_POINTY_NW, Sprite.WALL_DIRECTIONAL_POINTY_NW,
                               "resources/graphics/hyrule_wall_pointy_corner_nw.png", [0, 0])

def _register_directional_wall(wall_type, sprite, sprite_sheet_path, sprite_sheet_index):
    register_entity_sprite_map(
        sprite, SpriteSheet(sprite_sheet_path), (21, 21), (25, 25),
        {Direction.DOWN: [sprite_sheet_index]}, (0, 0))
    register_wall_data(wall_type, WallData(sprite, (25, 25)))


def _register_statue():
    sprite = Sprite.WALL_STATUE
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    indices_by_dir = {Direction.DOWN: [(13, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-4, -54))
    register_wall_data(WallType.STATUE, WallData(sprite, (42, 46)))

def _register_chair():
    sprite = Sprite.WALL_CHAIR
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(7, 0)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
    register_wall_data(WallType.WALL_CHAIR, WallData(sprite, (50, 50)))