#!/usr/bin/env python3
from pythongame.core.game_data import CONSUMABLES, \
    get_consumables_with_level, get_items_with_level, get_item_data_by_type
from pythongame.register_game_data import register_all_game_data


def print_loot():
    for level in range(1, 10):
        consumable_types = get_consumables_with_level(level)
        item_types = get_items_with_level(level)
        if not consumable_types and not item_types:
            continue
        print("LEVEL " + str(level))
        print("- - - - -")
        for c_type in consumable_types:
            print("{:<25}".format(c_type.name) + str(CONSUMABLES[c_type].description))
        for i_type in item_types:
            data = get_item_data_by_type(i_type)
            # TODO print more than custom description
            print("{:<25}".format(i_type) + str(data.custom_description_lines))
        print("")


register_all_game_data()
print_loot()
