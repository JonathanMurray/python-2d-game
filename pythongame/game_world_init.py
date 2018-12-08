from typing import Optional, Dict, List

from pythongame.core.common import *
from pythongame.core.enemy_behavior import create_enemy_mind
from pythongame.core.game_data import WALL_SIZE, ENEMIES, POTION_ENTITY_SPRITES
from pythongame.core.game_state import WorldEntity, Enemy, GameState, PotionOnGround
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.player_data import PLAYER_ENTITY_SIZE, INTIAL_PLAYER_STATE, PLAYER_ENTITY_SPEED
from pythongame.potion_health import POTION_ENTITY_SIZE

GRID_CELL_SIZE = 25


class MapFileEntity:
    def __init__(self, enemy_type: Optional[EnemyType], is_player: bool, is_wall: bool,
                 potion_type: Optional[PotionType]):
        self.enemy_type = enemy_type
        self.is_player = is_player
        self.is_wall = is_wall
        self.potion_type = potion_type

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        # No need for efficiency in this class
        return 0

    @staticmethod
    def player():
        return MapFileEntity(None, True, False, None)

    @staticmethod
    def enemy(enemy_type: EnemyType):
        return MapFileEntity(enemy_type, False, False, None)

    @staticmethod
    def wall():
        return MapFileEntity(None, False, True, None)

    # TODO handle more potions
    @staticmethod
    def potion(potion_type: PotionType):
        return MapFileEntity(None, False, False, potion_type)


MAP_FILE_ENTITIES_BY_CHAR: Dict[str, MapFileEntity] = {
    'P': MapFileEntity.player(),
    'X': MapFileEntity.wall(),
    'D': MapFileEntity.enemy(EnemyType.DARK_REAPER),
    'R': MapFileEntity.enemy(EnemyType.RAT_1),
    '2': MapFileEntity.enemy(EnemyType.RAT_2),
    'H': MapFileEntity.potion(PotionType.HEALTH),
    'M': MapFileEntity.potion(PotionType.MANA),
    'W': MapFileEntity.enemy(EnemyType.GOBLIN_WARLOCK),
    'U': MapFileEntity.enemy(EnemyType.MUMMY)
}

CHARS_BY_MAP_FILE_ENTITY: Dict[MapFileEntity, str] = {v: k for k, v in MAP_FILE_ENTITIES_BY_CHAR.items()}


def create_game_state_from_file(camera_size: Tuple[int, int], map_file: str):
    positions_by_map_file_entity: Dict[MapFileEntity, List[Tuple[int, int]]] = {}
    max_col_index = 0
    max_row_index = 0
    with open(map_file) as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (col_index * GRID_CELL_SIZE, row_index * GRID_CELL_SIZE)
                if char in MAP_FILE_ENTITIES_BY_CHAR:
                    map_file_entity = MAP_FILE_ENTITIES_BY_CHAR[char]
                    if not map_file_entity in positions_by_map_file_entity:
                        positions_by_map_file_entity[map_file_entity] = []
                    positions_by_map_file_entity[map_file_entity].append(game_world_pos)
                col_index += 1
                if char != '\n':
                    max_col_index = max(col_index, max_col_index)
            row_index += 1
            max_row_index = max(row_index, max_row_index)

    player_pos = positions_by_map_file_entity[MapFileEntity.player()][0]
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)

    potions = []
    for char in MAP_FILE_ENTITIES_BY_CHAR.keys():
        entity = MAP_FILE_ENTITIES_BY_CHAR[char]
        if entity.potion_type:
            potions += [_create_potion_at_position(entity.potion_type, pos)
                        for pos in positions_by_map_file_entity.get(entity, [])]

    path_finder = GlobalPathFinder()
    enemies = []
    for char in MAP_FILE_ENTITIES_BY_CHAR.keys():
        entity = MAP_FILE_ENTITIES_BY_CHAR[char]
        if entity.enemy_type:
            enemies += [_create_enemy_at_position(entity.enemy_type, pos, path_finder)
                        for pos in positions_by_map_file_entity.get(entity, [])]

    wall_positions = positions_by_map_file_entity.get(MapFileEntity.wall(), [])
    walls = [WorldEntity(pos, WALL_SIZE, Sprite.WALL) for pos in wall_positions]

    game_world_size = (max_col_index * GRID_CELL_SIZE, max_row_index * GRID_CELL_SIZE)
    game_state = GameState(player_entity, potions, enemies, walls, camera_size, game_world_size, INTIAL_PLAYER_STATE)
    path_finder.set_grid(game_state.grid)
    return game_state


def save_game_state_to_file(game_state: GameState, map_file: str):
    grid = {}
    game_world_size = game_state.game_world_size
    # + 1 to account for entities that were placed right on the border of the game world
    grid_num_cols = game_world_size[0] // GRID_CELL_SIZE + 1
    grid_num_rows = game_world_size[1] // GRID_CELL_SIZE + 1

    for e in game_state.enemies:
        enemy_type = e.enemy_type
        grid_position = (e.world_entity.x // GRID_CELL_SIZE, e.world_entity.y // GRID_CELL_SIZE)
        grid[grid_position] = MapFileEntity.enemy(enemy_type)

    player_grid_position = game_state.player_entity.x // GRID_CELL_SIZE, game_state.player_entity.y // GRID_CELL_SIZE
    grid[player_grid_position] = MapFileEntity.player()

    for w in game_state.walls:
        grid_position = (w.x // GRID_CELL_SIZE, w.y // GRID_CELL_SIZE)
        grid[grid_position] = MapFileEntity.wall()

    for p in game_state.potions_on_ground:
        grid_position = (p.world_entity.x // GRID_CELL_SIZE, p.world_entity.y // GRID_CELL_SIZE)
        grid[grid_position] = MapFileEntity.potion(p.potion_type)

    with open(map_file, 'w') as map_file:
        for row_index in range(grid_num_rows):
            for col_index in range(grid_num_cols):
                if (col_index, row_index) in grid:
                    entity_in_cell = grid[(col_index, row_index)]
                    char = CHARS_BY_MAP_FILE_ENTITY[entity_in_cell]
                    map_file.write(char)
                else:
                    map_file.write(" ")
            map_file.write("\n")


def _create_enemy_at_position(enemy_type: EnemyType, pos: Tuple[int, int], global_path_finder: GlobalPathFinder):
    data = ENEMIES[enemy_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    enemy_mind = create_enemy_mind(enemy_type, global_path_finder)
    return Enemy(enemy_type, entity, data.max_health, data.max_health, data.health_regen, enemy_mind)


def _create_potion_at_position(potion_type: PotionType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_SPRITES[potion_type])
    return PotionOnGround(entity, potion_type)
