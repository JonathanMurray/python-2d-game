from common import *


def create_projectile_controller(projectile_behavior):
    if projectile_behavior == ProjectileType.PLAYER:
        return PlayerProjectileController()
    if projectile_behavior == ProjectileType.PLAYER_AOE:
        return PlayerAoeProjectileController()
    if projectile_behavior == ProjectileType.ENEMY_POISON:
        return EnemyPoisonProjectileController()


class PlayerProjectileController:
    def apply_enemy_collision(self, enemy):
        enemy.lose_health(3)


class PlayerAoeProjectileController:
    def apply_enemy_collision(self, enemy):
        enemy.lose_health(2)


class EnemyPoisonProjectileController:
    def apply_player_collision(self, game_state):
        game_state.player_state.lose_health(1)
        game_state.player_state.add_buff(BuffType.DAMAGE_OVER_TIME, 2000)
