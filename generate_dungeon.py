#!/usr/bin/env python3
import random
from typing import Optional

from pythongame.core.common import NpcType
from pythongame.core.entity_creation import create_npc
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, NpcCategory
from pythongame.core.game_state import NonPlayerCharacter
from pythongame.dungeon_generator import DungeonGenerator
from pythongame.map_file import write_json_to_file
from pythongame.register_game_data import register_all_game_data

register_all_game_data()


def main():
    # Prefer maps that are longer on the horizontal axis, due to the aspect ratio of the in-game camera
    w = random.randint(100, 130)
    world_size = (w, 200 - w)
    dungeon_generator = DungeonGenerator(
        world_size=world_size,
        max_num_rooms=15,
        room_allowed_width=(8, 25),
        room_allowed_height=(8, 25),
        corridor_allowed_width=(2, 6),
        generate_npc=generate_npc, )
    grid, rooms = dungeon_generator.generate_random_grid()
    json = dungeon_generator.generate_random_map_as_json_from_grid(grid, rooms)
    write_json_to_file(json, "resources/maps/dudmap.json")


def generate_npc(x: int, y: int) -> Optional[NonPlayerCharacter]:
    npc_types = list(NpcType.__members__.values())
    valid_enemy_types = [npc_type for npc_type in npc_types
                         if NON_PLAYER_CHARACTERS[npc_type].npc_category == NpcCategory.ENEMY
                         and npc_type != NpcType.DARK_REAPER]
    if random.random() < 0.2:
        npc_type = random.choice(valid_enemy_types)
        return create_npc(npc_type, (x, y))


if __name__ == "__main__":
    main()
