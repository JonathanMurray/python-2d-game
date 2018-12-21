from pythongame.core.common import WallType, Sprite, Direction
from pythongame.core.game_data import register_wall_data, WallData, register_entity_sprite_map, SpriteSheet

WALL_SIZE = (25, 25)


def register_walls():
    register_wall_data(WallType.WALL, WallData(Sprite.WALL, WALL_SIZE))
    sprite_sheet = SpriteSheet("resources/graphics/stone_tile.png")
    original_sprite_size = (410, 404)
    scaled_sprite_size = (WALL_SIZE[0] - 1, WALL_SIZE[1] - 1)
    indices_by_dir = {
        Direction.DOWN: [(0, 0)]
    }
    register_entity_sprite_map(Sprite.WALL, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (1, 1))
