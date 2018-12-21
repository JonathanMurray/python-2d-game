import json
from typing import Optional, Dict

from pythongame.core.common import *
from pythongame.core.enemy_creation import create_enemy, set_global_path_finder
from pythongame.core.game_data import POTIONS, ITEM_ENTITY_SIZE, ITEMS, WALLS
from pythongame.core.game_state import WorldEntity, GameState, PotionOnGround, ItemOnGround, DecorationEntity, Wall
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.player_data import PLAYER_ENTITY_SIZE, INTIAL_PLAYER_STATE, PLAYER_ENTITY_SPEED
from pythongame.game_data.potion_health import POTION_ENTITY_SIZE

# TODO Avoid depending on pythongame.game_data from here

GRID_CELL_SIZE = 25


class MapFileEntity:
    def __init__(self, enemy_type: Optional[EnemyType], is_player: bool, wall_type: WallType,
                 potion_type: Optional[PotionType], item_type: Optional[ItemType], decoration_sprite: Optional[Sprite]):
        self.enemy_type = enemy_type
        self.is_player = is_player
        self.wall_type = wall_type
        self.potion_type = potion_type
        self.item_type = item_type
        self.decoration_sprite = decoration_sprite

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        # No need for efficiency in this class
        return 0

    @staticmethod
    def player():
        return MapFileEntity(None, True, None, None, None, None)

    @staticmethod
    def enemy(enemy_type: EnemyType):
        return MapFileEntity(enemy_type, False, None, None, None, None)

    @staticmethod
    def wall(wall_type: WallType):
        return MapFileEntity(None, False, wall_type, None, None, None)

    @staticmethod
    def potion(potion_type: PotionType):
        return MapFileEntity(None, False, None, potion_type, None, None)

    @staticmethod
    def item(item_type: ItemType):
        return MapFileEntity(None, False, None, None, item_type, None)

    @staticmethod
    def decoration(sprite: Sprite):
        return MapFileEntity(None, False, None, None, None, sprite)


MAP_FILE_ENTITIES_BY_CHAR: Dict[str, MapFileEntity] = {
    'P': MapFileEntity.player(),
    'X': MapFileEntity.wall(WallType.WALL),
    'D': MapFileEntity.enemy(EnemyType.DARK_REAPER),
    'R': MapFileEntity.enemy(EnemyType.RAT_1),
    '2': MapFileEntity.enemy(EnemyType.RAT_2),
    'H': MapFileEntity.potion(PotionType.HEALTH),
    'M': MapFileEntity.potion(PotionType.MANA),
    'W': MapFileEntity.enemy(EnemyType.GOBLIN_WARLOCK),
    'U': MapFileEntity.enemy(EnemyType.MUMMY),
    'A': MapFileEntity.enemy(EnemyType.NECROMANCER),

    'B': MapFileEntity.item(ItemType.WINGED_BOOTS),
    'O': MapFileEntity.item(ItemType.SWORD_OF_LEECHING),
    'L': MapFileEntity.item(ItemType.ROD_OF_LIGHTNING),
    'E': MapFileEntity.item(ItemType.AMULET_OF_MANA),

    'G': MapFileEntity.decoration(Sprite.DECORATION_GROUND_STONE),
    'T': MapFileEntity.decoration(Sprite.DECORATION_STATUE),
    'N': MapFileEntity.decoration(Sprite.DECORATION_PLANT)
}

CHARS_BY_MAP_FILE_ENTITY: Dict[MapFileEntity, str] = {v: k for k, v in MAP_FILE_ENTITIES_BY_CHAR.items()}


# def create_game_state_from_file(camera_size: Tuple[int, int], map_file: str):
#     positions_by_map_file_entity: Dict[MapFileEntity, List[Tuple[int, int]]] = {}
#     max_col_index = 0
#     max_row_index = 0
#     with open(map_file) as map_file:
#         row_index = 0
#         for line in map_file:
#             col_index = 0
#             for char in line:
#                 game_world_pos = (col_index * GRID_CELL_SIZE, row_index * GRID_CELL_SIZE)
#                 if char in MAP_FILE_ENTITIES_BY_CHAR:
#                     map_file_entity = MAP_FILE_ENTITIES_BY_CHAR[char]
#                     if not map_file_entity in positions_by_map_file_entity:
#                         positions_by_map_file_entity[map_file_entity] = []
#                     positions_by_map_file_entity[map_file_entity].append(game_world_pos)
#                 col_index += 1
#                 if char != '\n':
#                     max_col_index = max(col_index, max_col_index)
#             row_index += 1
#             max_row_index = max(row_index, max_row_index)
#
#     player_pos = positions_by_map_file_entity[MapFileEntity.player()][0]
#     player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)
#
#     potions = []
#     items = []
#     for char in MAP_FILE_ENTITIES_BY_CHAR.keys():
#         entity = MAP_FILE_ENTITIES_BY_CHAR[char]
#         if entity.potion_type:
#             potions += [_create_potion_at_position(entity.potion_type, pos)
#                         for pos in positions_by_map_file_entity.get(entity, [])]
#         elif entity.item_type:
#             items += [_create_item_at_position(entity.item_type, pos)
#                       for pos in positions_by_map_file_entity.get(entity, [])]
#
#     path_finder = GlobalPathFinder()
#     set_global_path_finder(path_finder)
#     enemies = []
#     for char in MAP_FILE_ENTITIES_BY_CHAR.keys():
#         entity = MAP_FILE_ENTITIES_BY_CHAR[char]
#         if entity.enemy_type:
#             enemies += [create_enemy(entity.enemy_type, pos)
#                         for pos in positions_by_map_file_entity.get(entity, [])]
#
#     wall_positions = positions_by_map_file_entity.get(MapFileEntity.wall(), [])
#     walls = [WorldEntity(pos, WALL_SIZE, Sprite.WALL) for pos in wall_positions]
#
#     game_world_size = (max_col_index * GRID_CELL_SIZE, max_row_index * GRID_CELL_SIZE)
#     game_state = GameState(player_entity, potions, items, enemies, walls, camera_size, game_world_size,
#                            INTIAL_PLAYER_STATE)
#     path_finder.set_grid(game_state.grid)
#     return game_state


def create_game_state_from_json_file(camera_size: Tuple[int, int], map_file: str):
    with open(map_file) as map_file:
        json_data = json.loads(map_file.read())

        player_pos = json_data["player"]["position"]
        player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)

        potions = [_create_potion_at_position(PotionType[p["potion_type"]], p["position"]) for p in
                   json_data["potions_on_ground"]]
        items = [_create_item_at_position(ItemType[i["item_type"]], i["position"]) for i in
                 json_data["items_on_ground"]]

        path_finder = GlobalPathFinder()
        set_global_path_finder(path_finder)
        enemies = [create_enemy(EnemyType[e["enemy_type"]], e["position"]) for e in json_data["enemies"]]

        walls = [_create_wall_at_position(WallType[w["wall_type"]], w["position"]) for w in json_data["walls"]]

        game_world_size = json_data["game_world_size"]

        decoration_entities = [DecorationEntity(d["position"], Sprite[d["sprite"]]) for d in json_data["decorations"]]
        game_state = GameState(player_entity, potions, items, enemies, walls, camera_size, game_world_size,
                               INTIAL_PLAYER_STATE, decoration_entities)
        path_finder.set_grid(game_state.grid)
        return game_state


#
# def save_game_state_to_file(game_state: GameState, map_file: str):
#     grid = {}
#     game_world_size = game_state.game_world_size
#     # + 1 to account for entities that were placed right on the border of the game world
#     grid_num_cols = game_world_size[0] // GRID_CELL_SIZE + 1
#     grid_num_rows = game_world_size[1] // GRID_CELL_SIZE + 1
#
#     for e in game_state.enemies:
#         enemy_type = e.enemy_type
#         grid_position = (e.world_entity.x // GRID_CELL_SIZE, e.world_entity.y // GRID_CELL_SIZE)
#         grid[grid_position] = MapFileEntity.enemy(enemy_type)
#
#     player_grid_position = game_state.player_entity.x // GRID_CELL_SIZE, game_state.player_entity.y // GRID_CELL_SIZE
#     grid[player_grid_position] = MapFileEntity.player()
#
#     for w in game_state.walls:
#         grid_position = (w.x // GRID_CELL_SIZE, w.y // GRID_CELL_SIZE)
#         grid[grid_position] = MapFileEntity.wall()
#
#     for p in game_state.potions_on_ground:
#         grid_position = (p.world_entity.x // GRID_CELL_SIZE, p.world_entity.y // GRID_CELL_SIZE)
#         grid[grid_position] = MapFileEntity.potion(p.potion_type)
#
#     for i in game_state.items_on_ground:
#         grid_position = (i.world_entity.x // GRID_CELL_SIZE, i.world_entity.y // GRID_CELL_SIZE)
#         grid[grid_position] = MapFileEntity.item(i.item_type)
#
#     with open(map_file, 'w') as map_file:
#         for row_index in range(grid_num_rows):
#             for col_index in range(grid_num_cols):
#                 if (col_index, row_index) in grid:
#                     entity_in_cell = grid[(col_index, row_index)]
#                     char = CHARS_BY_MAP_FILE_ENTITY[entity_in_cell]
#                     map_file.write(char)
#                 else:
#                     map_file.write(" ")
#             map_file.write("\n")


def save_game_state_to_json_file(game_state: GameState, map_file: str):
    json_data = {}

    json_data["enemies"] = []
    for e in game_state.enemies:
        json_data["enemies"].append({"enemy_type": e.enemy_type.name, "position": e.world_entity.get_position()})

    json_data["player"] = {"position": game_state.player_entity.get_position()}

    json_data["walls"] = []
    for w in game_state.walls:
        json_data["walls"].append({"wall_type": w.wall_type.name, "position": w.world_entity.get_position()})

    json_data["potions_on_ground"] = []
    for p in game_state.potions_on_ground:
        json_data["potions_on_ground"].append(
            {"potion_type": p.potion_type.name, "position": p.world_entity.get_position()})

    json_data["items_on_ground"] = []
    for i in game_state.items_on_ground:
        json_data["items_on_ground"].append({"item_type": i.item_type.name, "position": i.world_entity.get_position()})

    json_data["decorations"] = []
    for d in game_state.decoration_entities:
        json_data["decorations"].append({"sprite": d.sprite.name, "position": d.get_position()})

    json_data["game_world_size"] = game_state.game_world_size

    with open(map_file, 'w') as map_file:
        map_file.write(json.dumps(json_data, indent=2))


def _create_potion_at_position(potion_type: PotionType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, POTIONS[potion_type].entity_sprite)
    return PotionOnGround(entity, potion_type)


def _create_item_at_position(item_type: ItemType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, ITEM_ENTITY_SIZE, ITEMS[item_type].entity_sprite)
    return ItemOnGround(entity, item_type)


def _create_wall_at_position(wall_type: WallType, pos: Tuple[int, int]) -> Wall:
    return Wall(wall_type, WorldEntity(pos, WALLS[wall_type].size, WALLS[wall_type].sprite))
