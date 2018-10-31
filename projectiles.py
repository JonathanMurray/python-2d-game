from common import *


def create_projectile_controller(projectile_behavior):
    if projectile_behavior == ProjectileType.PLAYER:
        return PlayerProjectileController()
    if projectile_behavior == ProjectileType.PLAYER_AOE:
        return PlayerAoeProjectileController()
    if projectile_behavior == ProjectileType.ENEMY_POISON:
        return EnemyPoisonProjectileController()


class PlayerProjectileController:
    def __init__(self):
        self.age = 0

    def notify_time_passed(self, projectile, time_passed):
        self.age += time_passed
        if self.age > 3000:
            projectile.has_expired = True

    def apply_enemy_collision(self, enemy):
        enemy.lose_health(3)
        return True


class PlayerAoeProjectileController:
    def __init__(self):
        self.has_activated = False
        self.age = 0

    def notify_time_passed(self, projectile, time_passed):
        self.age += time_passed
        if self.age > 250:
            self.has_activated = True
        if self.age > 500:
            projectile.has_expired = True

    def apply_enemy_collision(self, enemy):
        if self.has_activated:
            enemy.lose_health(2)
        return self.has_activated


class EnemyPoisonProjectileController:
    def __init__(self):
        self.age = 0

    def notify_time_passed(self, projectile, time_passed):
        self.age += time_passed
        if self.age > 2000:
            projectile.has_expired = True

    def apply_player_collision(self, game_state):
        game_state.player_state.lose_health(1)
        game_state.player_state.add_buff(BuffType.DAMAGE_OVER_TIME, 2000)
