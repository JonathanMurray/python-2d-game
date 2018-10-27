from common import *


def apply_potion_effect(potion_type, game_state):
    player_state = game_state.player_state
    if potion_type == PotionType.HEALTH:
        player_state.gain_health(100)
    elif potion_type == PotionType.MANA:
        player_state.gain_mana(25)
    elif potion_type == PotionType.SPEED:
        if not player_state.has_effect_speed:
            game_state.player_entity.add_to_speed_multiplier(1)
        player_state.has_effect_speed = True
        player_state.time_until_speed_expires = 1500
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
