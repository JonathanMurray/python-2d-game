from pythongame.common import *
from pythongame.game_state import Projectile, Enemy, GameState
from pythongame.visual_effects import VisualCircle


def create_projectile_controller(projectile_type: ProjectileType):
    if projectile_type == ProjectileType.PLAYER:
        return PlayerProjectileController()
    if projectile_type == ProjectileType.PLAYER_AOE:
        return PlayerAoeProjectileController()
    if projectile_type == ProjectileType.ENEMY_POISON:
        return EnemyPoisonProjectileController()
    if projectile_type == ProjectileType.PLAYER_MAGIC_MISSILE:
        return PlayerMagicMissileProjectileController()


class AbstractProjectileController:
    def __init__(self, max_age):
        self._age = 0
        self._max_age = max_age

    def notify_time_passed(self, _game_state: GameState, projectile: Projectile, time_passed: Millis):
        self._age += time_passed
        if self._age > self._max_age:
            projectile.has_expired = True

    def apply_enemy_collision(self, _enemy: Enemy, _game_state: GameState):
        return False

    def apply_player_collision(self, _game_state: GameState):
        return False


class PlayerProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(3000)

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        enemy.lose_health(3)
        game_state.visual_effects.append(VisualCircle((250, 100, 50), enemy.world_entity.get_center_position(), 45,
                                                      Millis(100), 0))
        return True


class PlayerAoeProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)
        self._dmg_cooldown = 150
        self._time_since_dmg = self._dmg_cooldown

    def notify_time_passed(self, game_state: GameState, projectile: Projectile, time_passed: Millis):
        super().notify_time_passed(game_state, projectile, time_passed)
        self._time_since_dmg += time_passed
        if self._time_since_dmg > self._dmg_cooldown:
            self._time_since_dmg = False
            for enemy in game_state.get_enemies_intersecting_with(projectile.world_entity):
                enemy.lose_health(1)


class PlayerMagicMissileProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(400)
        self._enemies_hit = []

    def apply_enemy_collision(self, enemy: Enemy, game_state: GameState):
        if enemy not in self._enemies_hit:
            enemy.lose_health(1)
            game_state.visual_effects.append(VisualCircle((250, 100, 250), enemy.world_entity.get_center_position(), 25,
                                                          Millis(100), 0))
            self._enemies_hit.append(enemy)
        return False


class EnemyPoisonProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState):
        game_state.player_state.lose_health(1)
        game_state.player_state.gain_buff(BuffType.DAMAGE_OVER_TIME, Millis(2000))
        game_state.visual_effects.append(VisualCircle((50, 180, 50), game_state.player_entity.get_center_position(),
                                                      50, Millis(100), 0))
        return True
