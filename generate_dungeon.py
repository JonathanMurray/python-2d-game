#!/usr/bin/env python3

import random
from enum import Enum
from typing import List, Tuple

from pygame.rect import Rect

from pythongame.core.common import WallType, Sprite, NpcType
from pythongame.core.entity_creation import create_wall, create_decoration_entity, create_npc
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, NpcCategory
from pythongame.map_file import MapJson, save_map_data_to_file
from pythongame.register_game_data import register_all_game_data

register_all_game_data()

MAP_SIZE = (150, 150)
MAX_ROOM_ATTEMPTS = 100
MAX_NUM_ROOMS = 15
ROOM_ALLOWED_WIDTH = (8, 25)
ROOM_ALLOWED_HEIGHT = (8, 25)
CORRIDOR_ALLOWED_WIDTH = (2, 6)

CELL_SIZE = (25, 25)


class CellType(Enum):
    NONE = 0
    ROOM = 1
    CORRIDOR = 2
    WALL = 3
    REMOVED_WALL = 4


class Grid:
    def __init__(self, grid: List[List[CellType]]):
        self._grid = grid

    @staticmethod
    def create(map_size: Tuple[int, int], rooms: List[Rect], corridors: List[Rect]):
        _grid = []
        grid = Grid(_grid)
        for y in range(map_size[0]):
            _grid.append([CellType.NONE] * map_size[1])

        for room in rooms:
            for y in range(room.y, room.y + room.h):
                for x in range(room.x, room.x + room.w):
                    _grid[x][y] = CellType.ROOM

        for corridor in corridors:
            for y in range(corridor.y, corridor.y + corridor.h):
                for x in range(corridor.x, corridor.x + corridor.w):
                    _grid[x][y] = CellType.CORRIDOR

        for x in range(MAP_SIZE[0]):
            for y in range(MAP_SIZE[1]):
                is_empty = grid._is_cell((x, y), [CellType.NONE])
                neighbours_room_or_corridor = \
                    grid.is_walkable((x, y - 1)) or \
                    grid.is_walkable((x + 1, y - 1)) or \
                    grid.is_walkable((x + 1, y)) or \
                    grid.is_walkable((x + 1, y + 1)) or \
                    grid.is_walkable((x, y + 1)) or \
                    grid.is_walkable((x - 1, y + 1)) or \
                    grid.is_walkable((x - 1, y)) or \
                    grid.is_walkable((x - 1, y - 1))
                if is_empty and neighbours_room_or_corridor:
                    _grid[x][y] = CellType.WALL

        grid.prune_bad_walls()

        return grid

    def print(self):
        for y in range(MAP_SIZE[1]):
            for x in range(MAP_SIZE[0]):
                cell = "* " if self._grid[x][y] == CellType.ROOM else "  "
                print(cell, end='')
            print()

    def cell(self, x: int, y: int):
        return self._grid[x][y]

    def _is_cell(self, cell: Tuple[int, int], targets: List[CellType]):
        x, y = cell
        if 0 <= x < MAP_SIZE[0]:
            if 0 <= y < MAP_SIZE[1]:
                return self._grid[x][y] in targets
        return False

    def is_wall(self, cell: Tuple[int, int]):
        return self._is_cell(cell, [CellType.WALL])

    def is_walkable(self, cell: Tuple[int, int]):
        return self._is_cell(cell, [CellType.ROOM, CellType.CORRIDOR, CellType.REMOVED_WALL])

    def prune_bad_walls(self):
        for y in range(MAP_SIZE[1]):
            for x in range(MAP_SIZE[0]):
                # Thin wall segments that are "inside" walkable areas, cannot be rendered in a good way given the
                # sprites we are using, so we remove any such segments.
                is_wall = self.is_wall((x, y))
                is_thin_vertical_wall = is_wall and self.is_walkable((x - 1, y)) and self.is_walkable((x + 1, y))
                is_thin_horizontal_wall = is_wall and self.is_walkable((x, y - 1)) and self.is_walkable((x, y + 1))
                if is_thin_vertical_wall:
                    print("Pruning cell (%i, %i) (part of vertical line)" % (x, y))
                    self._grid[x][y] = CellType.REMOVED_WALL
                if is_thin_horizontal_wall:
                    print("Pruning cell (%i, %i) (part of horizontal line)" % (x, y))
                    self._grid[x][y] = CellType.REMOVED_WALL


def generate_room() -> Rect:
    w = random.randint(ROOM_ALLOWED_WIDTH[0], ROOM_ALLOWED_HEIGHT[1] + 1)
    h = random.randint(ROOM_ALLOWED_HEIGHT[0], ROOM_ALLOWED_HEIGHT[1] + 1)
    x = random.randint(1, MAP_SIZE[0] - w - 3)
    y = random.randint(1, MAP_SIZE[1] - h - 3)
    return Rect(x, y, w, h)


def generate_corridor_between_rooms(room1: Rect, room2: Rect) -> List[Rect]:
    x1, y1 = room1.x + room1.w // 2, room1.y + room1.h // 2
    x2, y2 = room2.x + room2.w // 2, room2.y + room2.h // 2

    width = random.randint(CORRIDOR_ALLOWED_WIDTH[0], CORRIDOR_ALLOWED_WIDTH[1] + 1)

    ver_rect = Rect(x1 - (width - 1) // 2, min(y1, y2) - (width - 1) // 2, width, abs(y1 - y2) + width)
    hor_rect = Rect(min(x1, x2) - (width - 1) // 2, y2 - (width - 1) // 2, abs(x1 - x2) + width, width)

    return [ver_rect, hor_rect]


def generate_rooms_and_corridors() -> Tuple[List[Rect], List[Rect]]:
    print("Generating rooms and corridors...")
    rooms = []
    for _ in range(MAX_ROOM_ATTEMPTS):
        new_room = generate_room()
        collision = any(r for r in rooms if are_rooms_too_close(r, new_room))
        if collision:
            print("Skipping room, as it collides with existing room.")
        else:
            print("Room generated.")
            rooms.append(new_room)
        if len(rooms) == MAX_NUM_ROOMS:
            break
    print("Generated %i rooms." % len(rooms))
    corridors = []
    for i in range(len(rooms) - 1):
        corridor = generate_corridor_between_rooms(rooms[i], rooms[i + 1])
        corridors += corridor
    corridors += generate_corridor_between_rooms(rooms[-1], rooms[0])
    print("Generated %i corridors." % len(corridors))
    return rooms, corridors


def are_rooms_too_close(room1: Rect, room2: Rect):
    return room1.inflate(2, 2).colliderect(room2.inflate(2, 2))


def get_room_center(room: Rect):
    return (room.x + room.w // 2) * CELL_SIZE[0], (room.y + room.h // 2) * CELL_SIZE[1]


def determine_wall_type(grid: Grid, cell: Tuple[int, int]) -> WallType:
    x, y = cell
    w = (x - 1, y)
    e = (x + 1, y)
    s = (x, y + 1)
    n = (x, y - 1)
    se = (x + 1, y + 1)
    ne = (x + 1, y - 1)
    sw = (x - 1, y + 1)
    nw = (x - 1, y - 1)

    # straights:
    if grid.is_wall(w) and grid.is_wall(e) and grid.is_walkable(s):
        return WallType.WALL_DIRECTIONAL_N
    if grid.is_wall(w) and grid.is_wall(e) and grid.is_walkable(n):
        return WallType.WALL_DIRECTIONAL_S
    if grid.is_wall(n) and grid.is_wall(s) and grid.is_walkable(e):
        return WallType.WALL_DIRECTIONAL_W
    if grid.is_wall(n) and grid.is_wall(s) and grid.is_walkable(w):
        return WallType.WALL_DIRECTIONAL_E

    # diagonals:
    if grid.is_wall(w) and grid.is_wall(n):
        if grid.is_walkable(se) and grid.is_walkable(s) and grid.is_walkable(e):
            return WallType.WALL_DIRECTIONAL_POINTY_NW
        elif grid.is_walkable(nw):
            return WallType.WALL_DIRECTIONAL_SE
    if grid.is_wall(w) and grid.is_wall(s):
        if grid.is_walkable(ne) and grid.is_walkable(n) and grid.is_walkable(e):
            return WallType.WALL_DIRECTIONAL_POINTY_SW
        elif grid.is_walkable(sw):
            return WallType.WALL_DIRECTIONAL_NE
    if grid.is_wall(e) and grid.is_wall(n):
        if grid.is_walkable(sw) and grid.is_walkable(s) and grid.is_walkable(w):
            return WallType.WALL_DIRECTIONAL_POINTY_NE
        elif grid.is_walkable(ne):
            return WallType.WALL_DIRECTIONAL_SW
    if grid.is_wall(e) and grid.is_wall(s):
        if grid.is_walkable(nw) and grid.is_walkable(n) and grid.is_walkable(w):
            return WallType.WALL_DIRECTIONAL_POINTY_SE
        elif grid.is_walkable(se):
            return WallType.WALL_DIRECTIONAL_NW

    # default (couldn't find a fitting wall type)
    print("ERROR: Couldn't find fitting wall type for cell: " + str(cell))
    return WallType.WALL


def generate_random_map_as_json():
    rooms, corridors = generate_rooms_and_corridors()
    print("Rooms: ")
    print(rooms)

    grid = Grid.create(MAP_SIZE, rooms, corridors)

    walls = []
    decorations = []
    npcs = []

    for y in range(MAP_SIZE[1]):
        for x in range(MAP_SIZE[0]):
            position = (x * CELL_SIZE[0], y * CELL_SIZE[1])
            if grid.is_walkable((x, y)):
                decorations.append(create_decoration_entity(position, Sprite.DECORATION_GROUND_STONE))
            elif grid.is_wall((x, y)):
                wall_type = determine_wall_type(grid, (x, y))
                walls.append(create_wall(wall_type, position))

    world_area = Rect(0, 0, MAP_SIZE[0] * CELL_SIZE[0], MAP_SIZE[1] * CELL_SIZE[1])

    start_room = random.choice(rooms)
    player_position = get_room_center(start_room)

    for room in [r for r in rooms if r != start_room]:
        npc_types = list(NpcType.__members__.values())
        enemy_types = [npc_type for npc_type in npc_types
                       if NON_PLAYER_CHARACTERS[npc_type].npc_category == NpcCategory.ENEMY]
        npc_type = random.choice(enemy_types)
        npc = create_npc(npc_type, get_room_center(room))
        npcs.append(npc)

    json = MapJson.serialize_from_data(walls, decorations, [], world_area, player_position, npcs)
    return json


def main():
    json = generate_random_map_as_json()
    save_map_data_to_file(json, "resources/maps/dudmap.json")


if __name__ == "__main__":
    main()
