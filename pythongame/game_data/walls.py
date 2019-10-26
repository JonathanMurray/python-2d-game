from pythongame.core.common import WallType, Sprite, Direction
from pythongame.core.game_data import register_wall_data, WallData, register_entity_sprite_map
from pythongame.core.view.image_loading import SpriteSheet


def register_walls():
    _register_wall()
    _register_statue()
    _register_directional_walls()
    _register_chair()
    _register_altar()
    _register_shelves()
    _register_barrels()


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


def _register_altar():
    sprite = Sprite.WALL_ALTAR
    sprite_sheet = SpriteSheet("resources/graphics/wall_altar.png")
    original_sprite_size = (88, 38)
    scaled_sprite_size = (100, 50)
    indices_by_dir = {Direction.DOWN: [(0, 0)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir, (0, -13))
    register_wall_data(WallType.ALTAR, WallData(sprite, (100, 25)))  # table is roughly 13px tall


def _register_chair():
    sprite = Sprite.WALL_CHAIR
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices_by_dir = {Direction.DOWN: [(7, 0)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (0, 0))
    register_wall_data(WallType.WALL_CHAIR, WallData(sprite, (50, 50)))


def _register_shelves():
    sprites = [Sprite.WALL_SHELF_EMPTY, Sprite.WALL_SHELF_HELMETS, Sprite.WALL_SHELF_ARMORS]
    wall_types = [WallType.SHELF_EMPTY, WallType.SHELF_HELMETS, WallType.SHELF_ARMORS]
    indices = [(1, 0), (1, 1), (1, 2)]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (64, 32)
    scaled_sprite_size = (100, 50)
    for i in range(3):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -25))
        register_wall_data(wall_types[i], WallData(sprites[i], (100, 25)))


def _register_barrels():
    sprites = [Sprite.WALL_BARREL_1, Sprite.WALL_BARREL_2, Sprite.WALL_BARREL_3, Sprite.WALL_BARREL_4,
               Sprite.WALL_BARREL_5, Sprite.WALL_BARREL_6]
    wall_types = [WallType.BARREL_1, WallType.BARREL_2, WallType.BARREL_3, WallType.BARREL_4, WallType.BARREL_5,
                  WallType.BARREL_6]
    indices = [(3, 11), (3, 12), (4, 11), (4, 12), (5, 11), (5, 12)]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    for i in range(6):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -25))
        register_wall_data(wall_types[i], WallData(sprites[i], (50, 25)))
