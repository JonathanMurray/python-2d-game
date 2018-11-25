from typing import Optional

from pythongame.core.common import *
from pythongame.core.enemy_behavior import create_enemy_mind
from pythongame.core.game_data import WALL_SIZE, ENEMIES
from pythongame.core.game_state import WorldEntity, Enemy, GameState, PotionOnGround
from pythongame.player_data import PLAYER_ENTITY_SIZE, INTIAL_PLAYER_STATE
from pythongame.potion_health import POTION_ENTITY_SIZE

PLAYER_ENTITY_SPEED = 0.13

GRID_CELL_SIZE = 25


def create_game_state_from_file(camera_size: Tuple[int, int], map_file: str):
    dumb_enemy_positions = []
    smart_enemy_positions = []
    mage_enemy_positions = []
    potion_positions = []
    player_pos = (0, 0)
    berserker_positions = []
    wall_positions = []
    rat_1_positions = []
    rat_2_positions = []
    max_col_index = 0
    max_row_index = 0
    with open(map_file) as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (col_index * GRID_CELL_SIZE, row_index * GRID_CELL_SIZE)
                if char == 'P':
                    player_pos = game_world_pos
                if char == 'D':
                    dumb_enemy_positions.append(game_world_pos)
                if char == 'S':
                    smart_enemy_positions.append(game_world_pos)
                if char == 'M':
                    mage_enemy_positions.append(game_world_pos)
                if char == 'H':
                    potion_positions.append(game_world_pos)
                if char == 'B':
                    berserker_positions.append(game_world_pos)
                if char == 'R':
                    rat_1_positions.append(game_world_pos)
                if char == '2':
                    rat_2_positions.append(game_world_pos)
                if char == 'X':
                    wall_positions.append(game_world_pos)
                col_index += 1
                if char != '\n':
                    max_col_index = max(col_index, max_col_index)
            row_index += 1
            max_row_index = max(row_index, max_row_index)
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)
    potions = [PotionOnGround(WorldEntity(pos, POTION_ENTITY_SIZE, Sprite.HEALTH_POTION), PotionType.HEALTH)
               for pos in potion_positions]
    dumb_enemies = [_create_enemy_at_position(EnemyType.DUMB, pos) for pos in dumb_enemy_positions]
    smart_enemies = [_create_enemy_at_position(EnemyType.SMART, pos) for pos in smart_enemy_positions]
    mage_enemies = [_create_enemy_at_position(EnemyType.MAGE, pos) for pos in mage_enemy_positions]
    berserker_enemies = [_create_enemy_at_position(EnemyType.BERSERKER, pos) for pos in berserker_positions]
    rat_1_enemies = [_create_enemy_at_position(EnemyType.RAT_1, pos) for pos in rat_1_positions]
    rat_2_enemies = [_create_enemy_at_position(EnemyType.RAT_2, pos) for pos in rat_2_positions]
    walls = [WorldEntity(pos, WALL_SIZE, Sprite.WALL) for pos in wall_positions]
    enemies = dumb_enemies + smart_enemies + mage_enemies + berserker_enemies + rat_1_enemies + rat_2_enemies

    game_world_size = (max_col_index * GRID_CELL_SIZE, max_row_index * GRID_CELL_SIZE)
    return GameState(player_entity, potions, enemies, walls, camera_size, game_world_size, INTIAL_PLAYER_STATE)


class MapFileEntity:
    def __init__(self, enemy_type: Optional[EnemyType], is_player: bool, is_wall: bool):
        self.enemy_type = enemy_type
        self.is_player = is_player
        self.is_wall = is_wall


def save_game_state_to_file(game_state: GameState, map_file: str):
    grid = {}
    game_world_size = game_state.game_world_size
    grid_num_cols = game_world_size[0] // GRID_CELL_SIZE
    grid_num_rows = game_world_size[1] // GRID_CELL_SIZE

    for e in game_state.enemies:
        enemy_type = e.enemy_type
        grid_position = (e.world_entity.x // GRID_CELL_SIZE, e.world_entity.y // GRID_CELL_SIZE)
        grid[grid_position] = MapFileEntity(enemy_type, False, False)

    player_grid_position = game_state.player_entity.x // GRID_CELL_SIZE, game_state.player_entity.y // GRID_CELL_SIZE
    grid[player_grid_position] = MapFileEntity(None, True, False)

    for w in game_state.walls:
        grid_position = (w.x // GRID_CELL_SIZE, w.y // GRID_CELL_SIZE)
        grid[grid_position] = MapFileEntity(None, False, True)

    with open(map_file, 'w') as map_file:
        for row_index in range(grid_num_rows):
            for col_index in range(grid_num_cols):
                if (col_index, row_index) in grid:
                    entity_in_cell = grid[(col_index, row_index)]
                    if entity_in_cell.enemy_type:
                        if entity_in_cell.enemy_type == EnemyType.RAT_2:
                            map_file.write("2")
                        elif entity_in_cell.enemy_type == EnemyType.RAT_1:
                            map_file.write("R")
                    elif entity_in_cell.is_player:
                        map_file.write("P")
                    elif entity_in_cell.is_wall:
                        map_file.write("X")
                else:
                    map_file.write(" ")
            map_file.write("\n")


def _create_enemy_at_position(enemy_type: EnemyType, pos: Tuple[int, int]):
    data = ENEMIES[enemy_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    return Enemy(enemy_type, entity, data.max_health, data.max_health, create_enemy_mind(enemy_type))
