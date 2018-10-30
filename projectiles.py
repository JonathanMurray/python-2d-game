from common import *


def apply_projectile_enemy_collision_effect(projectile_type, enemy):
    if projectile_type == ProjectileType.PLAYER:
        enemy.lose_health(3)
    if projectile_type == ProjectileType.PLAYER_AOE:
        enemy.lose_health(2)


def apply_projectile_player_collision_effect(game_state):
    game_state.player_state.lose_health(1)
    game_state.player_state.add_buff(BuffType.DAMAGE_OVER_TIME, 2000)
