from pythongame.common import *
from pythongame.game_state import Projectile, Enemy, GameState


def create_projectile_controller(projectile_type: ProjectileType):
    if projectile_type == ProjectileType.PLAYER:
        return PlayerProjectileController()
    if projectile_type == ProjectileType.PLAYER_AOE:
        return PlayerAoeProjectileController()
    if projectile_type == ProjectileType.ENEMY_POISON:
        return EnemyPoisonProjectileController()


class AbstractProjectileController:
    def __init__(self, max_age):
        self._age = 0
        self._max_age = max_age

    def notify_time_passed(self, projectile: Projectile, time_passed: Millis):
        self._age += time_passed
        if self._age > self._max_age:
            projectile.has_expired = True

    def apply_enemy_collision(self, _):
        return False

    def apply_player_collision(self, _):
        return False


class PlayerProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(3000)

    def apply_enemy_collision(self, enemy: Enemy):
        enemy.lose_health(3)
        return True


class PlayerAoeProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(500)
        self._has_activated = False

    def notify_time_passed(self, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(projectile, time_passed)
        if self._age > 250:
            self._has_activated = True

    def apply_enemy_collision(self, enemy: Enemy):
        if self._has_activated:
            enemy.lose_health(2)
            return True
        return False


class EnemyPoisonProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState):
        game_state.player_state.lose_health(1)
        game_state.player_state.add_buff(BuffType.DAMAGE_OVER_TIME, Millis(2000))
        return True
