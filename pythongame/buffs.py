from pythongame.common import *
from pythongame.game_data import MAGIC_MISSILE_PROJECTILE_SIZE
from pythongame.game_state import GameState, WorldEntity, Projectile
from pythongame.projectiles import create_projectile_controller
from pythongame.visual_effects import VisualCircle, VisualRect, create_visual_damage_text, create_visual_healing_text


class AbstractBuff:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass


class HealingOverTime(AbstractBuff):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_graphics += time_passed
        healing_amount = 0.04
        game_state.player_state.gain_health(healing_amount * time_passed)
        if self._time_since_graphics > 500:
            estimate_health_gained = int(self._time_since_graphics * healing_amount)
            game_state.visual_effects.append(
                create_visual_healing_text(game_state.player_entity, estimate_health_gained))
            game_state.visual_effects.append(
                VisualCircle((200, 200, 50), game_state.player_entity.get_center_position(),
                             10, Millis(100), 0))
            self._time_since_graphics = 0


class DamageOverTime(AbstractBuff):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_graphics += time_passed
        damage_per_ms = 0.02
        game_state.player_state.lose_health(damage_per_ms * time_passed)
        graphics_cooldown = 300
        if self._time_since_graphics > graphics_cooldown:
            game_state.visual_effects.append(VisualCircle((50, 180, 50), game_state.player_entity.get_center_position(),
                                                          20, Millis(50), 0, game_state.player_entity))
            estimate_damage_taken = int(damage_per_ms * graphics_cooldown)
            game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, estimate_damage_taken))
            self._time_since_graphics = 0


class IncreasedMoveSpeed(AbstractBuff):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(1)

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 100:
            game_state.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.player_entity.get_center_position(), 10, Millis(200), 0))
            self._time_since_graphics = 0

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-1)


class Invisibility(AbstractBuff):
    def __init__(self):
        self._time_since_graphics = 0

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.is_invisible = True

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_graphics += time_passed
        if self._time_since_graphics > 320:
            self._time_since_graphics = 0
            game_state.visual_effects.append(
                VisualRect((0, 0, 250), game_state.player_entity.get_center_position(), 60, Millis(400),
                           game_state.player_entity))

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.is_invisible = False


class ChannelingMagicMissiles(AbstractBuff):
    def __init__(self):
        self._time_since_firing = 0

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.is_stunned = True
        game_state.player_entity.set_not_moving()

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        self._time_since_firing += time_passed
        if self._time_since_firing > 150:
            self._time_since_firing = 0
            player_center_position = game_state.player_entity.get_center_position()
            projectile_pos = get_position_from_center_position(player_center_position, MAGIC_MISSILE_PROJECTILE_SIZE)
            entity = WorldEntity(projectile_pos, MAGIC_MISSILE_PROJECTILE_SIZE, Sprite.MAGIC_MISSILE,
                                 game_state.player_entity.direction, 0.5)
            projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_MAGIC_MISSILE))
            game_state.projectile_entities.append(projectile)
            game_state.visual_effects.append(VisualRect((250, 0, 250), player_center_position, 60, Millis(250)))

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.is_stunned = False


BUFF_EFFECTS = {
    BuffType.HEALING_OVER_TIME: HealingOverTime(),
    BuffType.DAMAGE_OVER_TIME: DamageOverTime(),
    BuffType.INCREASED_MOVE_SPEED: IncreasedMoveSpeed(),
    BuffType.INVISIBILITY: Invisibility(),
    BuffType.CHANNELING_MAGIC_MISSILES: ChannelingMagicMissiles()
}
