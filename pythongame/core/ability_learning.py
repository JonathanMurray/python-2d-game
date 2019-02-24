import pygame

from pythongame.core.common import AbilityType
from pythongame.core.game_data import register_user_ability_key, UserAbilityKey
from pythongame.core.game_state import PlayerState

USER_ABILITY_KEYS = [UserAbilityKey("Q", pygame.K_q),
                     UserAbilityKey("W", pygame.K_w),
                     UserAbilityKey("E", pygame.K_e),
                     UserAbilityKey("R", pygame.K_r)]


def player_learn_new_ability(player_state: PlayerState, ability_type: AbilityType):
    player_state.gain_ability(ability_type)
    num_abilities = len(player_state.abilities)
    user_ability_key = USER_ABILITY_KEYS[num_abilities - 1]
    register_user_ability_key(ability_type, user_ability_key)
