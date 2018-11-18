from pythongame.core.common import *
from pythongame.core.enemy_behavior import create_enemy_mind
from pythongame.core.game_data import PLAYER_ENTITY_SIZE, WALL_SIZE, ENEMIES
from pythongame.core.game_state import WorldEntity, Enemy, GameState, PotionOnGround, PlayerState
from pythongame.potion_health import POTION_ENTITY_SIZE

PLAYER_ENTITY_SPEED = 0.13


def init_game_state_from_file(camera_size: Tuple[int, int]):
    dumb_enemy_positions = []
    smart_enemy_positions = []
    mage_enemy_positions = []
    potion_positions = []
    player_pos = (0, 0)
    berserker_positions = []
    wall_positions = []
    col_width = 50
    row_height = 50
    max_col_index = 0
    max_row_index = 0
    MAP_FILE = "resources/maps/pathfinding_test.txt"
    #MAP_FILE = "resources/maps/load_test_10k_walls_160_enemies.txt"
    with open(MAP_FILE) as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (col_index * col_width, row_index * row_height)
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
    walls = [WorldEntity(pos, WALL_SIZE, Sprite.WALL) for pos in wall_positions]
    enemies = dumb_enemies + smart_enemies + mage_enemies + berserker_enemies
    player_potion_slots = {
        1: PotionType.SPEED,
        2: PotionType.MANA,
        3: PotionType.HEALTH,
        4: PotionType.INVISIBILITY,
        5: PotionType.INVISIBILITY
    }

    abilities = [AbilityType.ATTACK, AbilityType.HEAL, AbilityType.AOE_ATTACK, AbilityType.CHANNEL_ATTACK,
                 AbilityType.TELEPORT]
    player_state = PlayerState(300, 300, 90, 100, 0.002, player_potion_slots, abilities)
    game_world_size = (max_col_index * col_width, max_row_index * row_height)
    return GameState(player_entity, potions, enemies, walls, camera_size, game_world_size, player_state)


def _create_enemy_at_position(enemy_type: EnemyType, pos: Tuple[int, int]):
    data = ENEMIES[enemy_type]
    entity = WorldEntity(pos, data.size, data.sprite, Direction.LEFT, data.speed)
    return Enemy(entity, data.max_health, data.max_health, create_enemy_mind(enemy_type))
