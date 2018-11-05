from pythongame.common import *
from pythongame.game_state import GameState
from pythongame.visual_effects import VisualCircle, create_visual_damage_text


class AbstractBuff:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass


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


BUFF_EFFECTS = {
    BuffType.DAMAGE_OVER_TIME: DamageOverTime(),
}


def register_buff_effect(buff_type: BuffType, effect: AbstractBuff):
    BUFF_EFFECTS[buff_type] = effect
