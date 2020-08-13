#!/usr/bin/env python3
from pythongame.core.abilities import ABILITIES
from pythongame.core.common import AbilityType
from pythongame.register_game_data import register_all_game_data


def print_abilities():
    for ability_type in AbilityType:
        ability_data = ABILITIES[ability_type]
        print("{:<25}".format(ability_type.name) + str(ability_data.description))


register_all_game_data()
print_abilities()
