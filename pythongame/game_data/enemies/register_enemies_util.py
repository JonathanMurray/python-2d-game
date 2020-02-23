from typing import Dict, List, Tuple, Type

from pythongame.core.common import NpcType, Direction
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind


def register_basic_enemy(
        npc_type: NpcType,
        npc_data: NpcData,
        mind_constructor: Type[AbstractNpcMind],
        spritesheet_path: str,
        original_sprite_size: Tuple[int, int],
        scaled_sprite_size: Tuple[int, int],
        spritesheet_indices: Dict[Direction, List[Tuple[int, int]]],
        sprite_position_relative_to_entity: Tuple[int, int]):
    register_npc_data(npc_type, npc_data)
    register_npc_behavior(npc_type, mind_constructor)
    sprite_sheet = SpriteSheet(spritesheet_path)
    register_entity_sprite_map(npc_data.sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               spritesheet_indices,
                               sprite_position_relative_to_entity)
