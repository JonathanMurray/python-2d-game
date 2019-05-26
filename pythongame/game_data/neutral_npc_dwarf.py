import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 1200
        self._time_since_updated_path = self._update_path_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_updated_path += time_passed
        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if random.random() > 0.5:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


def register_dwarf_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_DWARF
    npc_type = NpcType.NEUTRAL_DWARF
    movement_speed = 0.03
    health = 6
    register_npc_data(npc_type, NpcData(sprite, size, health, 0, movement_speed, 4, False, True))
    register_npc_behavior(npc_type, NpcMind)
    sprite_sheet = SpriteSheet("resources/graphics/skeleton_sprite_map.png")
    original_sprite_size = (32, 48)
    scaled_sprite_size = (48, 72)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -42))
