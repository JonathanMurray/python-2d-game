#!/usr/bin/env python3

from pythongame.dungeon_generator import DungeonGenerator
from pythongame.map_file import write_json_to_file
from pythongame.register_game_data import register_all_game_data

register_all_game_data()


def main():
    dungeon_generator = DungeonGenerator()
    grid, rooms = dungeon_generator.generate_random_grid()
    json = dungeon_generator.generate_random_map_as_json_from_grid(grid, rooms)
    write_json_to_file(json, "resources/maps/dudmap.json")


if __name__ == "__main__":
    main()
