from pythongame.core.common import AbilityType
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_state import PlayerState


def player_learn_new_ability(player_state: PlayerState, ability_type: AbilityType):
    player_state.gain_ability(ability_type)
    allocate_input_keys_for_abilities(player_state.abilities)
