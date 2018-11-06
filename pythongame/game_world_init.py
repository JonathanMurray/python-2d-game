from pythongame.common import *
from pythongame.enemy_behavior import create_enemy_mind
from pythongame.game_data import PLAYER_ENTITY_SIZE, POTION_ENTITY_SIZE, WALL_SIZE, ENEMY_SIZES
from pythongame.game_state import WorldEntity, Enemy, GameState, PotionOnGround, PlayerState

ENEMY_SPEED = 0.02
ENEMY_2_SPEED = 0.032
ENEMY_MAGE_SPEED = 0.02
PLAYER_ENTITY_SPEED = 0.13
ENEMY_BERSERKER_SPEED = 0.1


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
    with open("resources/map.txt") as map_file:
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
                max_col_index = max(col_index, max_col_index)
            row_index += 1
            max_row_index = max(row_index, max_row_index)
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)
    potions = [PotionOnGround(WorldEntity(pos, POTION_ENTITY_SIZE, Sprite.HEALTH_POTION), PotionType.HEALTH)
               for pos in potion_positions]
    dumb_enemies = [
        Enemy(WorldEntity(pos, ENEMY_SIZES[EnemyType.DUMB], Sprite.ENEMY, Direction.LEFT, ENEMY_SPEED), 5, 5,
              create_enemy_mind(EnemyType.DUMB)) for pos in dumb_enemy_positions]
    smart_enemies = [
        Enemy(WorldEntity(pos, ENEMY_SIZES[EnemyType.SMART], Sprite.ENEMY_2, Direction.LEFT, ENEMY_2_SPEED), 9, 9,
              create_enemy_mind(EnemyType.SMART)) for pos in smart_enemy_positions]
    mage_enemies = [
        Enemy(WorldEntity(pos, ENEMY_SIZES[EnemyType.MAGE], Sprite.ENEMY_MAGE, Direction.LEFT, ENEMY_MAGE_SPEED),
              25, 25, create_enemy_mind(EnemyType.MAGE)) for pos in mage_enemy_positions]
    berserker_enemies = [
        Enemy(WorldEntity(pos, ENEMY_SIZES[EnemyType.BERSERKER], Sprite.ENEMY_BERSERKER, Direction.LEFT,
                          ENEMY_BERSERKER_SPEED),
              25, 25, create_enemy_mind(EnemyType.BERSERKER)) for pos in berserker_positions]
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
