from common import *


class AbstractBuff:
    def apply_start_effect(self, game_state):
        pass

    def apply_middle_effect(self, game_state):
        pass

    def apply_end_effect(self, game_state):
        pass


class HealingOverTime(AbstractBuff):
    def apply_middle_effect(self, game_state):
        game_state.player_state.gain_health(1)


class DamageOverTime(AbstractBuff):
    def apply_middle_effect(self, game_state):
        game_state.player_state.lose_health(1)


class IncreasedMoveSpeed(AbstractBuff):
    def apply_start_effect(self, game_state):
        game_state.player_entity.add_to_speed_multiplier(1)

    def apply_end_effect(self, game_state):
        game_state.player_entity.add_to_speed_multiplier(-1)


BUFF_EFFECTS = {
    BuffType.HEALING_OVER_TIME: HealingOverTime(),
    BuffType.DAMAGE_OVER_TIME: DamageOverTime(),
    BuffType.INCREASED_MOVE_SPEED: IncreasedMoveSpeed()
}
