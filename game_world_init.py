from game_state import WorldEntity, Enemy, PlayerAbilityStats, GameState
from common import Direction

COLOR_ATTACK_PROJECTILE = (200, 5, 200)
POTION_ENTITY_SIZE = (30, 30)
POTION_ENTITY_COLOR = (50, 200, 50)
ENEMY_SIZE = (30, 30)
ENEMY_COLOR = (250, 0, 0)
ENEMY_SPEED = 0.4
PLAYER_ENTITY_SIZE = (50, 50)
PLAYER_ENTITY_COLOR = (250, 250, 250)
PLAYER_ENTITY_SPEED = 2
ATTACK_PROJECTILE_SIZE = (35, 35)
ATTACK_PROJECTILE_SPEED = 4
HEAL_ABILITY_MANA_COST = 10
HEAL_ABILITY_AMOUNT = 10
ATTACK_ABILITY_MANA_COST = 5


def init_game_state_from_file(game_world_size, camera_size):
    enemy_positions = []
    potion_positions = []
    player_pos = (0, 0)
    with open("map.txt") as map_file:
        row_index = 0
        for line in map_file:
            col_index = 0
            for char in line:
                game_world_pos = (game_world_size[0] * col_index / 100, game_world_size[1] * row_index / 50)
                if char == 'P':
                    player_pos = game_world_pos
                if char == 'E':
                    enemy_positions.append(game_world_pos)
                if char == 'H':
                    potion_positions.append(game_world_pos)
                col_index += 1
            row_index += 1
    player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, PLAYER_ENTITY_COLOR, Direction.RIGHT, 0,
                                PLAYER_ENTITY_SPEED)
    potion_entities = [WorldEntity(pos, POTION_ENTITY_SIZE, POTION_ENTITY_COLOR) for pos in potion_positions]
    enemies = [Enemy(WorldEntity(pos, ENEMY_SIZE, ENEMY_COLOR, Direction.LEFT, ENEMY_SPEED, ENEMY_SPEED), 2, 2)
               for pos in enemy_positions]
    player_ability_stats = PlayerAbilityStats(HEAL_ABILITY_MANA_COST, HEAL_ABILITY_AMOUNT, ATTACK_ABILITY_MANA_COST,
                                              ATTACK_PROJECTILE_SIZE, COLOR_ATTACK_PROJECTILE, ATTACK_PROJECTILE_SPEED)
    return GameState(player_entity, potion_entities, enemies, camera_size, game_world_size, player_ability_stats)
