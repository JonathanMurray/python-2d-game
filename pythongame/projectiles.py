from pythongame.common import *
from pythongame.game_state import Projectile, Enemy, GameState
from pythongame.visual_effects import VisualCircle, create_visual_damage_text


def create_projectile_controller(projectile_type: ProjectileType):
    return projectile_controllers[projectile_type]()


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


class EnemyPoisonProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState):
        damage_amount = 1
        game_state.player_state.lose_health(damage_amount)
        game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, damage_amount))
        game_state.player_state.gain_buff(BuffType.DAMAGE_OVER_TIME, Millis(2000))
        game_state.visual_effects.append(VisualCircle((50, 180, 50), game_state.player_entity.get_center_position(),
                                                      50, Millis(100), 0))
        return True


projectile_controllers = {
    ProjectileType.ENEMY_POISON: EnemyPoisonProjectileController,
}


def register_projectile_controller(projectile_type: ProjectileType, controller):
    projectile_controllers[projectile_type] = controller
