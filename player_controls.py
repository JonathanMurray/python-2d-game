from game_data import ABILITIES


# Returns ability_type if ability was used
# Returns None if not enough mana
def try_use_ability(player_state, ability_type):
    mana_cost = ABILITIES[ability_type].mana_cost
    if player_state.mana >= mana_cost:
        player_state.lose_mana(mana_cost)
        return True
    return False
