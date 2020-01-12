#!/usr/bin/env python3

import random
from ast import literal_eval
from enum import Enum
from typing import List, Tuple

from pygame.rect import Rect

from pythongame.core.common import WallType, Sprite, NpcType
from pythongame.core.entity_creation import create_wall, create_decoration_entity, create_npc
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, NpcCategory
from pythongame.core.game_state import DecorationEntity, Wall
from pythongame.map_file import MapJson, write_json_to_file
from pythongame.register_game_data import register_all_game_data

register_all_game_data()

MAX_ROOM_ATTEMPTS = 100
MAX_NUM_ROOMS = 15
ROOM_ALLOWED_WIDTH = (8, 25)
ROOM_ALLOWED_HEIGHT = (8, 25)
CORRIDOR_ALLOWED_WIDTH = (2, 6)

CELL_SIZE = 25


class CellType(Enum):
    NONE = 0
    FLOOR = 1
    WALL = 3


class Grid:
    def __init__(self, grid: List[List[CellType]], size: Tuple[int, int]):
        self._grid = grid
        self.size = size
        self._floor_cells = set()

    @staticmethod
    def create_from_rects(map_size: Tuple[int, int], walkable_areas: List[Rect]):

        print("Creating grid (%i, %i) from %i rects ..." % (map_size[0], map_size[1], len(walkable_areas)))
        _grid = []
        grid = Grid(_grid, map_size)
        for y in range(map_size[0]):
            _grid.append([CellType.NONE] * map_size[1])

        for rect in walkable_areas:
            for y in range(rect.y, rect.y + rect.h):
                for x in range(rect.x, rect.x + rect.w):
                    _grid[x][y] = CellType.FLOOR
                    grid._floor_cells.add((x, y))

        grid._update_wall_cells(range(0, grid.size[0]), range(0, grid.size[1]))
        grid._prune_bad_walls(range(0, grid.size[0]), range(0, grid.size[1]))

        print("Grid created")

        return grid

    def add_floor_cells(self, cells: List[Tuple[int, int]]):
        if not cells:
            return

        xmin = min([cell[0] for cell in cells]) - 1
        xmax = max([cell[0] for cell in cells]) + 2
        ymin = min([cell[1] for cell in cells]) - 1
        ymax = max([cell[1] for cell in cells]) + 2

        for cell in cells:
            self._grid[cell[0]][cell[1]] = CellType.FLOOR
            self._floor_cells.add(cell)
        self._update_wall_cells(range(xmin, xmax), range(ymin, ymax))
        self._prune_bad_walls(range(xmin, xmax), range(ymin, ymax))

    def remove_floor_cells(self, cells: List[Tuple[int, int]]):
        xmin = min([cell[0] for cell in cells]) - 1
        xmax = max([cell[0] for cell in cells]) + 2
        ymin = min([cell[1] for cell in cells]) - 1
        ymax = max([cell[1] for cell in cells]) + 2

        for cell in cells:
            self._grid[cell[0]][cell[1]] = CellType.NONE
            if cell in self._floor_cells:
                self._floor_cells.remove(cell)
        self._update_wall_cells(range(xmin, xmax), range(ymin, ymax))
        self._prune_bad_walls(range(xmin, xmax), range(ymin, ymax))

    def print(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                cell = "* " if self._grid[x][y] == CellType.FLOOR else \
                    ("x " if self._grid[x][y] == CellType.WALL else "  ")
                print(cell, end='')
            print()

    def cell(self, x: int, y: int):
        return self._grid[x][y]

    # TODO optimization: don't check bounds here. Let caller keep track of it!
    def _is_cell(self, cell: Tuple[int, int], target: CellType):
        x, y = cell
        if 0 <= x < self.size[0]:
            if 0 <= y < self.size[1]:
                return self._grid[x][y] == target
        return False

    def _is_within_grid(self, cell: Tuple[int, int]):
        return 0 <= cell[0] < self.size[0] and 0 <= cell[1] < self.size[1]

    def is_wall(self, cell: Tuple[int, int]):
        return self._is_cell(cell, CellType.WALL)

    def is_floor(self, cell: Tuple[int, int]):
        return self._is_cell(cell, CellType.FLOOR)

    def _update_wall_cells(self, xrange, yrange):
        # print("Updating wall cells...")

        cells_that_have_floor_neighbours = set()

        for (x, y) in self._floor_cells:
            cells_that_have_floor_neighbours.add((x, y - 1))
            cells_that_have_floor_neighbours.add((x + 1, y - 1))
            cells_that_have_floor_neighbours.add((x + 1, y))
            cells_that_have_floor_neighbours.add((x + 1, y + 1))
            cells_that_have_floor_neighbours.add((x, y + 1))
            cells_that_have_floor_neighbours.add((x - 1, y + 1))
            cells_that_have_floor_neighbours.add((x - 1, y))
            cells_that_have_floor_neighbours.add((x - 1, y - 1))

        xmin = min(xrange)
        xmax = max(xrange)
        ymin = min(yrange)
        ymax = max(yrange)

        for x in range(max(0, xmin), min(xmax + 1, self.size[0])):
            for y in range(max(0, ymin), min(ymax + 1, self.size[1])):
                cell = self._grid[x][y]
                if cell == CellType.FLOOR:
                    continue
                has_floor_neighbour = (x, y) in cells_that_have_floor_neighbours
                if has_floor_neighbour and cell == CellType.NONE:
                    self._grid[x][y] = CellType.WALL
                elif not has_floor_neighbour and cell == CellType.WALL:
                    self._grid[x][y] = CellType.NONE
        # print("done.")

    def _prune_bad_walls(self, xrange, yrange):
        # print("Pruning wall cells...")
        for x in xrange:
            for y in yrange:
                # Thin wall segments that are "inside" walkable areas, cannot be rendered in a good way given the
                # sprites we are using, so we remove any such segments.
                is_wall = self.is_wall((x, y))
                if is_wall and (
                        (self.is_floor((x - 1, y)) and self.is_floor((x + 1, y)))
                        or
                        (self.is_floor((x, y - 1)) and self.is_floor((x, y + 1)))
                ):
                    self._grid[x][y] = CellType.FLOOR
        # print("done.")

    def serialize(self) -> str:
        return str([[cell.value for cell in row] for row in self._grid])

    @staticmethod
    def deserialize(string: str):
        grid = [[CellType(cell) for cell in row] for row in literal_eval(string)]
        w = len(grid)
        h = len(grid[0])
        return Grid(grid, (w, h))


def generate_room(map_size: Tuple[int, int]) -> Rect:
    w = random.randint(ROOM_ALLOWED_WIDTH[0], ROOM_ALLOWED_HEIGHT[1] + 1)
    h = random.randint(ROOM_ALLOWED_HEIGHT[0], ROOM_ALLOWED_HEIGHT[1] + 1)
    x = random.randint(1, map_size[0] - w - 3)
    y = random.randint(1, map_size[1] - h - 3)
    return Rect(x, y, w, h)


def generate_corridor_between_rooms(room1: Rect, room2: Rect) -> List[Rect]:
    x1, y1 = room1.x + room1.w // 2, room1.y + room1.h // 2
    x2, y2 = room2.x + room2.w // 2, room2.y + room2.h // 2

    width = random.randint(CORRIDOR_ALLOWED_WIDTH[0], CORRIDOR_ALLOWED_WIDTH[1] + 1)

    ver_rect = Rect(x1 - (width - 1) // 2, min(y1, y2) - (width - 1) // 2, width, abs(y1 - y2) + width)
    hor_rect = Rect(min(x1, x2) - (width - 1) // 2, y2 - (width - 1) // 2, abs(x1 - x2) + width, width)

    return [ver_rect, hor_rect]


def generate_rooms_and_corridors(map_size: Tuple[int, int]) -> Tuple[List[Rect], List[Rect]]:
    rooms = []
    for _ in range(MAX_ROOM_ATTEMPTS):
        new_room = generate_room(map_size)
        collision = any(r for r in rooms if are_rooms_too_close(r, new_room))
        if collision:
            pass
        else:
            rooms.append(new_room)
        if len(rooms) == MAX_NUM_ROOMS:
            break
    corridors = []
    for i in range(len(rooms) - 1):
        corridor = generate_corridor_between_rooms(rooms[i], rooms[i + 1])
        corridors += corridor
    corridors += generate_corridor_between_rooms(rooms[-1], rooms[0])
    return rooms, corridors


def are_rooms_too_close(room1: Rect, room2: Rect):
    return room1.inflate(2, 2).colliderect(room2.inflate(2, 2))


def get_room_center(room: Rect):
    return (room.x + room.w // 2) * CELL_SIZE, (room.y + room.h // 2) * CELL_SIZE


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
    if grid.is_wall(w) and grid.is_wall(e) and grid.is_floor(s):
        return WallType.WALL_DIRECTIONAL_N
    if grid.is_wall(w) and grid.is_wall(e) and grid.is_floor(n):
        return WallType.WALL_DIRECTIONAL_S
    if grid.is_wall(n) and grid.is_wall(s) and grid.is_floor(e):
        return WallType.WALL_DIRECTIONAL_W
    if grid.is_wall(n) and grid.is_wall(s) and grid.is_floor(w):
        return WallType.WALL_DIRECTIONAL_E

    # diagonals:
    if grid.is_wall(w) and grid.is_wall(n):
        if grid.is_floor(se) and grid.is_floor(s) and grid.is_floor(e):
            return WallType.WALL_DIRECTIONAL_POINTY_NW
        elif grid.is_floor(nw):
            return WallType.WALL_DIRECTIONAL_SE
    if grid.is_wall(w) and grid.is_wall(s):
        if grid.is_floor(ne) and grid.is_floor(n) and grid.is_floor(e):
            return WallType.WALL_DIRECTIONAL_POINTY_SW
        elif grid.is_floor(sw):
            return WallType.WALL_DIRECTIONAL_NE
    if grid.is_wall(e) and grid.is_wall(n):
        if grid.is_floor(sw) and grid.is_floor(s) and grid.is_floor(w):
            return WallType.WALL_DIRECTIONAL_POINTY_NE
        elif grid.is_floor(ne):
            return WallType.WALL_DIRECTIONAL_SW
    if grid.is_wall(e) and grid.is_wall(s):
        if grid.is_floor(nw) and grid.is_floor(n) and grid.is_floor(w):
            return WallType.WALL_DIRECTIONAL_POINTY_SE
        elif grid.is_floor(se):
            return WallType.WALL_DIRECTIONAL_NW

    print("WARNING: Couldn't find fitting wall type for cell: " + str(cell))
    return WallType.WALL


def generate_random_grid() -> Tuple[Grid, List[Rect]]:
    # Prefer maps that are longer on the horizontal axis, due to the aspect ratio of the in-game camera
    w = random.randint(100, 130)
    map_size = (w, 200 - w)
    rooms, corridors = generate_rooms_and_corridors(map_size)

    grid = Grid.create_from_rects(map_size, rooms + corridors)
    return grid, rooms


def generate_random_map_as_json_from_grid(grid: Grid, rooms: List[Rect]):
    decorations, walls = create_floor_tiles_and_walls_from_grid(grid, (0, grid.size[0]), (0, grid.size[1]))

    world_area = Rect(0, 0, grid.size[0] * CELL_SIZE, grid.size[1] * CELL_SIZE)
    start_room = random.choice(rooms)
    player_position = get_room_center(start_room)

    npcs = generate_npcs(rooms, start_room)

    json = MapJson.serialize_from_data(walls, decorations, [], world_area, player_position, npcs)
    return json


def create_floor_tiles_and_walls_from_grid(grid: Grid, xrange: Tuple[int, int], yrange: Tuple[int, int]) -> Tuple[
    List[DecorationEntity], List[Wall]]:
    decorations: List[DecorationEntity] = []
    walls: List[Wall] = []

    for y in range(yrange[0], yrange[1]):
        for x in range(xrange[0], xrange[1]):
            position = (x * CELL_SIZE, y * CELL_SIZE)
            is_even_cell = x % 2 == 0 and y % 2 == 0  # ground sprite covers 4 cells, so we only need them on even cells
            if is_even_cell and any([grid.is_floor(c) for c in [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]]):
                decorations.append(create_decoration_entity(position, Sprite.DECORATION_GROUND_STONE))
            if grid.is_wall((x, y)):
                wall_type = determine_wall_type(grid, (x, y))
                walls.append(create_wall(wall_type, position))
    return decorations, walls


def generate_npcs(rooms: List[Rect], start_room: Rect):
    # TODO Check collisions, use more rules to spawn sensible enemy groups
    npcs = []
    npc_types = list(NpcType.__members__.values())
    valid_enemy_types = [npc_type for npc_type in npc_types
                         if NON_PLAYER_CHARACTERS[npc_type].npc_category == NpcCategory.ENEMY
                         and npc_type != NpcType.DARK_REAPER]
    for room in [r for r in rooms if r != start_room]:
        xmid, ymid = get_room_center(room)
        distance = CELL_SIZE * 2
        for x in range(xmid - distance, xmid + distance * 2, distance):
            for y in range(ymid - distance, ymid + distance * 2, distance):
                if random.random() < 0.2:
                    npc_type = random.choice(valid_enemy_types)
                    npc = create_npc(npc_type, (x, y))
                    npcs.append(npc)
    return npcs


def main():
    grid, rooms = generate_random_grid()
    json = generate_random_map_as_json_from_grid(grid, rooms)
    write_json_to_file(json, "resources/maps/dudmap.json")


if __name__ == "__main__":
    main()
