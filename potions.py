from common import *


def apply_potion_effect(potion_type, game_state):
    player_state = game_state.player_state
    if potion_type == PotionType.HEALTH:
        player_state.gain_health(100)
    elif potion_type == PotionType.MANA:
        player_state.gain_mana(25)
    elif potion_type == PotionType.SPEED:
        game_state.player_state.add_buff(BuffType.INCREASED_MOVE_SPEED, 3500)
    elif potion_type == PotionType.INVISIBILITY:
        game_state.player_state.add_buff(BuffType.INVISIBILITY, 5000)
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
