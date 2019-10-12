from pythongame.core.common import Millis, Sprite, Direction
from pythongame.core.game_data import SpriteSheet, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.loot import LootTable, LootGroup
from pythongame.core.npc_behaviors import AbstractNpcMind
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.loot_tables import LOOT_ITEMS_1, LOOT_ITEMS_2

CHEST_ENTITY_SIZE = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
CHEST_LOOT = LootTable([LootGroup(1, LOOT_ITEMS_1 + LOOT_ITEMS_2, 1)])


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        pass


def register_chest_enemy():
    sprite = Sprite.CHEST
    sprite_sheet = SpriteSheet("resources/graphics/human_tileset.png")
    original_sprite_size = (32, 64)
    scaled_sprite_size = (50, 75)
    indices_by_dir = {Direction.DOWN: [(9, 3)]}
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size,
                               indices_by_dir, (-6, -33))
