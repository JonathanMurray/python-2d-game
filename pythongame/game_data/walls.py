from pythongame.core.common import WallType, Sprite
from pythongame.core.game_data import register_wall_data, WallData, WALL_SIZE


def register_walls():

    # TODO move WALL_SIZE here
    register_wall_data(WallType.WALL, WallData(Sprite.WALL, WALL_SIZE))