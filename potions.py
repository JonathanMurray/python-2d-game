from common import *


# Returns any BuffType that should be applied
def apply_potion_effect(potion_type, game_state):
    player_state = game_state.player_state
    if potion_type == PotionType.HEALTH:
        player_state.gain_health(100)
        return None
    elif potion_type == PotionType.MANA:
        player_state.gain_mana(25)
        return None
    elif potion_type == PotionType.SPEED:
        buff_that_was_started = game_state.player_state.add_buff(BuffType.INCREASED_MOVE_SPEED, 3500)
        return buff_that_was_started
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
