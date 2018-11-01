from pythongame.common import *


class PotionWasConsumed:
    pass


class PotionFailedToBeConsumed:
    def __init__(self, reason):
        self.reason = reason


def try_consume_potion(potion_type, game_state):
    player_state = game_state.player_state
    if potion_type == PotionType.HEALTH:
        if game_state.player_state.health < game_state.player_state.max_health:
            player_state.gain_health(100)
            return PotionWasConsumed()
        else:
            return PotionFailedToBeConsumed("Already at full health!")
    elif potion_type == PotionType.MANA:
        if game_state.player_state.mana < game_state.player_state.max_mana:
            player_state.gain_mana(25)
            return PotionWasConsumed()
        else:
            return PotionFailedToBeConsumed("Already at full mana!")
    elif potion_type == PotionType.SPEED:
        game_state.player_state.add_buff(BuffType.INCREASED_MOVE_SPEED, 3500)
        return PotionWasConsumed()
    elif potion_type == PotionType.INVISIBILITY:
        game_state.player_state.add_buff(BuffType.INVISIBILITY, 5000)
        return PotionWasConsumed()
    else:
        raise Exception("Unhandled potion: " + str(potion_type))
