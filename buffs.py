from common import *


def apply_buff_start_effect(buff_type, game_state):
    if buff_type == BuffType.INCREASED_MOVE_SPEED:
        game_state.player_entity.add_to_speed_multiplier(1)


def apply_buff_middle_effect(buff_type, game_state):
    if buff_type == BuffType.HEALING_OVER_TIME:
        game_state.player_state.gain_health(1)
    elif buff_type == BuffType.DAMAGE_OVER_TIME:
        game_state.player_state.lose_health(1)


def apply_buff_end_effect(buff_type, game_state):
    if buff_type == BuffType.INCREASED_MOVE_SPEED:
        game_state.player_entity.add_to_speed_multiplier(-1)
