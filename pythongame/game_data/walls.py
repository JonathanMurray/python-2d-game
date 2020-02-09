from pythongame.core.common import WallType, Sprite, Direction
from pythongame.core.game_data import register_wall_data, WallData, register_entity_sprite_map, \
    register_entity_sprite_initializer
from pythongame.core.view.image_loading import SpriteSheet, SpriteInitializer


def register_walls():
    _register_wall()
    _register_statue()
    _register_directional_walls()
    _register_chairs()
    _register_altar()
    _register_shelves()
    _register_barrels()
    _register_baskets()
    _register_stone_crosses()
    _register_signs()
    _register_weapon_rack()
    _register_pillar()
    _register_light_pole()
    _register_well()
    _register_bench_mirror()
    _register_beds()
    _register_pillows()
    _register_decorated_table()


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


def _register_stone_crosses():
    sprites = [Sprite.WALL_STONE_CROSS_FLOWERS]
    wall_types = [WallType.STONE_CROSS_FLOWERS]
    indices = [(15, 3)]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 100)
    for i in range(len(sprites)):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (-7, -54))
        register_wall_data(wall_types[i], WallData(sprites[i], (42, 39)))


def _register_altar():
    sprite = Sprite.WALL_ALTAR
    sprite_sheet = SpriteSheet("resources/graphics/wall_altar.png")
    original_sprite_size = (88, 38)
    scaled_sprite_size = (100, 50)
    indices_by_dir = {Direction.DOWN: [(0, 0)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir, (0, -13))
    register_wall_data(WallType.ALTAR, WallData(sprite, (100, 25)))  # table is roughly 13px tall


def _register_chairs():
    sprites = [Sprite.WALL_CHAIR_DOWN, Sprite.WALL_CHAIR_UP, Sprite.WALL_CHAIR_RIGHT, Sprite.WALL_CHAIR_LEFT]
    wall_types = [WallType.CHAIR_DOWN, WallType.CHAIR_UP, WallType.CHAIR_RIGHT, WallType.CHAIR_LEFT]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    indices = [(4, 0), (5, 0), (6, 0), (7, 0)]
    for i in range(len(sprites)):
        indices_by_dir = {Direction.DOWN: [indices[i]]}
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   indices_by_dir, (0, 0))
        register_wall_data(wall_types[i], WallData(sprites[i], (50, 50)))


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
    for i in range(len(sprites)):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -25))
        register_wall_data(wall_types[i], WallData(sprites[i], (50, 25)))


def _register_baskets():
    sprites = [Sprite.WALL_BASKET_EMPTY, Sprite.WALL_BASKET_FRUIT]
    wall_types = [WallType.BASKET_EMPTY, WallType.BASKET_FRUIT]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    indices = [(4, 15), (5, 15)]
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    for i in range(len(sprites)):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -25))
        register_wall_data(wall_types[i], WallData(sprites[i], (50, 25)))


def _register_signs():
    sprites = [Sprite.WALL_SIGN_SMALL, Sprite.WALL_SIGN_MULTI, Sprite.WALL_SIGN_LARGE_EMPTY,
               Sprite.WALL_SIGN_LARGE_NOTES]
    wall_types = [WallType.SIGN_SMALL, WallType.SIGN_MULTI, WallType.SIGN_LARGE_EMPTY, WallType.SIGN_LARGE_NOTES]
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    indices = [(14, 2), (13, 2), (13, 1), (14, 1)]
    original_sprite_size = (32, 32)
    scaled_sprite_size = (50, 50)
    for i in range(len(sprites)):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -25))
        register_wall_data(wall_types[i], WallData(sprites[i], (50, 25)))


def _register_weapon_rack():
    register_entity_sprite_initializer(Sprite.WALL_WEAPON_RACK,
                                       SpriteInitializer("resources/graphics/wall_weapon_rack.png", (50, 100)),
                                       (0, -70))
    register_wall_data(WallType.WEAPON_RACK, WallData(Sprite.WALL_WEAPON_RACK, (50, 30)))


def _register_pillar():
    register_entity_sprite_initializer(Sprite.WALL_PILLAR,
                                       SpriteInitializer("resources/graphics/wall_pillar.png", (55, 110)),
                                       (0, -60))
    register_wall_data(WallType.PILLAR, WallData(Sprite.WALL_PILLAR, (50, 50)))


def _register_light_pole():
    register_entity_sprite_initializer(Sprite.WALL_LIGHT_POLE,
                                       SpriteInitializer("resources/graphics/wall_lightpole.png", (35, 105)),
                                       (0, -80))
    register_wall_data(WallType.LIGHT_POLE, WallData(Sprite.WALL_LIGHT_POLE, (35, 25)))


def _register_well():
    register_entity_sprite_initializer(Sprite.WALL_WELL,
                                       SpriteInitializer("resources/graphics/wall_well.png", (85, 75)),
                                       (0, -10))
    register_wall_data(WallType.WELL, WallData(Sprite.WALL_WELL, (75, 65)))


def _register_bench_mirror():
    register_entity_sprite_initializer(Sprite.WALL_BENCH_MIRROR,
                                       SpriteInitializer("resources/graphics/wall_bench_mirror.png", (35, 70)),
                                       (0, -50))
    register_wall_data(WallType.BENCH_MIRROR, WallData(Sprite.WALL_BENCH_MIRROR, (35, 20)))


def _register_beds():
    sprites = [Sprite.WALL_BED_1, Sprite.WALL_BED_2, Sprite.WALL_BED_3]
    wall_types = [WallType.BED_1, WallType.BED_2, WallType.BED_3]
    sprite_sheet = SpriteSheet("resources/graphics/wall_beds.png")
    indices = [(0, 0), (2, 0), (3, 0)]
    original_sprite_size = (32, 80)
    scaled_sprite_size = (36, 90)
    for i in range(len(sprites)):
        register_entity_sprite_map(sprites[i], sprite_sheet, original_sprite_size, scaled_sprite_size,
                                   {Direction.DOWN: [indices[i]]}, (0, -20))
        register_wall_data(wall_types[i], WallData(sprites[i], (36, 70)))


def _register_pillows():
    register_entity_sprite_initializer(Sprite.WALL_PILLOW,
                                       SpriteInitializer("resources/graphics/wall_pillow.png", (40, 30)),
                                       (0, 0))
    register_wall_data(WallType.PILLOW, WallData(Sprite.WALL_PILLOW, (40, 30)))
    register_entity_sprite_initializer(Sprite.WALL_PILLOWS_2,
                                       SpriteInitializer("resources/graphics/wall_pillows_2.png", (40, 35)),
                                       (0, -5))
    register_wall_data(WallType.PILLOWS_2, WallData(Sprite.WALL_PILLOWS_2, (40, 30)))


def _register_decorated_table():
    register_entity_sprite_initializer(Sprite.WALL_DECORATED_TABLE,
                                       SpriteInitializer("resources/graphics/wall_table_candles.png", (100, 75)),
                                       (-5, -35))
    register_wall_data(WallType.DECORATED_TABLE, WallData(Sprite.WALL_DECORATED_TABLE, (90, 40)))
