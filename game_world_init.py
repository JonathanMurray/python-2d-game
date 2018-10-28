from common import *
from game_data import PLAYER_ENTITY_SIZE, ENEMY_ENTITY_SIZE, ENEMY_2_ENTITY_SIZE
from game_state import WorldEntity, Enemy, GameState, Potion

POTION_ENTITY_SIZE = (30, 30)
POTION_ENTITY_COLOR = (50, 200, 50)
ENEMY_COLOR = (250, 0, 0)
ENEMY_SPEED = 0.4
ENEMY_2_COLOR = (200, 0, 0)
ENEMY_2_SPEED = 0.8
PLAYER_ENTITY_COLOR = (250, 250, 250)
PLAYER_ENTITY_SPEED = 2.7


def init_game_state_from_file(game_world_size, camera_size):
    dumb_enemy_positions = []
    smart_enemy_positions = []
    potion_positions = []
    player_pos = (0, 0)
    with open("resources/map.txt") as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (game_world_size[0] * col_index / 100, game_world_size[1] * row_index / 50)
                if char == 'P':
                    player_pos = game_world_pos
                if char == 'D':
                    dumb_enemy_positions.append(game_world_pos)
                if char == 'S':
                    smart_enemy_positions.append(game_world_pos)
                if char == 'H':
                    potion_positions.append(game_world_pos)
                col_index += 1
            row_index += 1
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, PLAYER_ENTITY_COLOR, Sprite.PLAYER, Direction.RIGHT, 0,
                                PLAYER_ENTITY_SPEED)
    potions = [Potion(WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_COLOR, None), PotionType.HEALTH)
               for pos in potion_positions]
    enemies = [Enemy(WorldEntity(pos, ENEMY_ENTITY_SIZE, ENEMY_COLOR, Sprite.ENEMY, Direction.LEFT, ENEMY_SPEED,
                                 ENEMY_SPEED), 2, 2, EnemyBehavior.DUMB) for pos in dumb_enemy_positions] + \
              [Enemy(WorldEntity(pos, ENEMY_2_ENTITY_SIZE, ENEMY_2_COLOR, Sprite.ENEMY_2, Direction.LEFT, ENEMY_2_SPEED,
                                 ENEMY_2_SPEED), 3, 3, EnemyBehavior.SMART) for pos in smart_enemy_positions]
    player_potion_slots = {
        1: PotionType.SPEED,
        2: PotionType.MANA,
        3: PotionType.HEALTH,
        4: PotionType.SPEED,
        5: PotionType.SPEED
    }
    return GameState(player_entity, potions, enemies, camera_size, game_world_size, player_potion_slots)
