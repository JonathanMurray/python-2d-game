#!/usr/bin/env python3
from pythongame.core.common import ConsumableType
from pythongame.core.game_data import CONSUMABLES, \
    get_optional_consumable_level
from pythongame.register_game_data import register_all_game_data


def print_consumables():
    entries = [(c_type, CONSUMABLES[c_type], get_optional_consumable_level(c_type))
               for c_type in ConsumableType]
    entries.sort(key=lambda entry: entry[2] if entry[2] else 9999)
    for c_type, c_data, c_level in entries:
        level_text = "level {:<10}".format(c_level) if c_level else " " * 16
        print("{:<25}".format(c_type.name) + level_text + str(c_data.description))
    print("")


register_all_game_data()
print_consumables()
