from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import BuffType, Millis, ProjectileType, Sprite
from pythongame.core.damage_interactions import deal_damage_to_player
from pythongame.core.game_data import register_buff_text, register_entity_sprite_initializer, SpriteInitializer
from pythongame.core.game_state import GameState, WorldEntity, Enemy
from pythongame.core.projectile_controllers import AbstractProjectileController, register_projectile_controller
from pythongame.core.visual_effects import create_visual_damage_text, VisualCircle

ENEMY_PROJECTILE_SIZE = (50, 50)


class EnemyPoisonProjectileController(AbstractProjectileController):
    def __init__(self):
        super().__init__(2000)

    def apply_player_collision(self, game_state: GameState):
        deal_damage_to_player(game_state, 1)
        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.DAMAGE_OVER_TIME), Millis(2000))
        game_state.visual_effects.append(VisualCircle((50, 180, 50), game_state.player_entity.get_center_position(),
                                                      25, 50, Millis(100), 0))
        return True


class DamageOverTime(AbstractBuffEffect):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_enemy: Enemy,
                            time_passed: Millis):
        self._time_since_graphics += time_passed
        damage_per_ms = 0.02
        deal_damage_to_player(game_state, damage_per_ms * float(time_passed))
        graphics_cooldown = 300
        if self._time_since_graphics > graphics_cooldown:
            game_state.visual_effects.append(VisualCircle((50, 180, 50), game_state.player_entity.get_center_position(),
                                                          10, 20, Millis(50), 0, game_state.player_entity))
            estimate_damage_taken = int(damage_per_ms * graphics_cooldown)
            game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, estimate_damage_taken))
            self._time_since_graphics = 0

    def get_buff_type(self):
        return BuffType.DAMAGE_OVER_TIME


def register_enemy_poison_projectile():
    register_projectile_controller(ProjectileType.ENEMY_POISON, EnemyPoisonProjectileController)
    register_entity_sprite_initializer(
        Sprite.POISONBALL, SpriteInitializer("resources/graphics/poisonball.png", ENEMY_PROJECTILE_SIZE))
    register_buff_effect(BuffType.DAMAGE_OVER_TIME, DamageOverTime)
    register_buff_text(BuffType.DAMAGE_OVER_TIME, "Poison")
