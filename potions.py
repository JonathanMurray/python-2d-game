from common import *


def apply_potion_effect(potion_type, game_state):
    player_state = game_state.player_state
    if potion_type == PotionType.HEALTH:
        player_state.gain_health(100)
    elif potion_type == PotionType.MANA:
        player_state.gain_mana(25)
    elif potion_type == PotionType.SPEED:
        should_apply_start_effect = game_state.player_state.add_buff(BuffType.INCREASED_MOVE_SPEED, 3500)
        # TODO move somewhere else
        if should_apply_start_effect:
            game_state.player_entity.add_to_speed_multiplier(1)
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
