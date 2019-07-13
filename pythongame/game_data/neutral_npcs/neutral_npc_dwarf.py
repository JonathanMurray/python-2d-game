import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite
from pythongame.core.damage_interactions import deal_damage_to_player
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    NpcDialog, register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, register_npc_action
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 900
        self._time_since_updated_path = self._update_path_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_updated_path += time_passed
        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


class NpcAction(AbstractNpcAction):

    def act(self, game_state: GameState) -> Optional[str]:
        deal_damage_to_player(game_state, 10)
        return "You take a beating!"


def register_dwarf_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_DWARF
    npc_type = NpcType.NEUTRAL_DWARF
    movement_speed = 0.03
    health = 6
    dialog = NpcDialog(
        "Hey there! You want a piece of me!? ",
        "Start a fight")
    register_npc_data(npc_type, NpcData(sprite, size, health, 0, movement_speed, 4, False, True, dialog,
                                        PortraitIconSprite.VIKING, None))
    register_npc_behavior(npc_type, NpcMind)
    register_npc_action(npc_type, NpcAction())
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(0, 4), (1, 4), (2, 4)],
        Direction.LEFT: [(0, 5), (1, 5), (2, 5)],
        Direction.RIGHT: [(0, 6), (1, 6), (2, 6)],
        Direction.UP: [(0, 7), (1, 7), (2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(PortraitIconSprite.VIKING, 'resources/graphics/viking_portrait.png')
