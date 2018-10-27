from common import *


def apply_potion_effect(potion_type, player_state):
    if potion_type == PotionType.HEALTH:
        player_state.gain_health(100)
    elif potion_type == PotionType.MANA:
        player_state.gain_mana(25)
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
