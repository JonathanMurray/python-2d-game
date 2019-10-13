from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_state import Projectile, NonPlayerCharacter, GameState


class AbstractProjectileController:
    def __init__(self, max_age):
        self._age = 0
        self._max_age = max_age

    def notify_time_passed(self, _game_state: GameState, projectile: Projectile, time_passed: Millis):
        self._age += time_passed
        if self._age > self._max_age:
            projectile.has_expired = True

    # Collision callbacks return a boolean that indicates whether or not the projectile should be removed.

    # Example: player's ability hits an enemy
    def apply_enemy_collision(self, _npc: NonPlayerCharacter, _game_state: GameState, _projectile: Projectile):
        pass

    def apply_player_summon_collision(self, _npc: NonPlayerCharacter, _game_state: GameState, _projectile: Projectile):
        pass

    # Example: enemy's ability hits player
    def apply_player_collision(self, _game_state: GameState, _projectile: Projectile):
        pass

    def apply_wall_collision(self, _game_state: GameState, _projectile: Projectile):
        pass


_projectile_controllers: Dict[ProjectileType, Type[AbstractProjectileController]] = {}


def register_projectile_controller(projectile_type: ProjectileType, controller: Type[AbstractProjectileController]):
    _projectile_controllers[projectile_type] = controller


def create_projectile_controller(projectile_type: ProjectileType):
    return _projectile_controllers[projectile_type]()
