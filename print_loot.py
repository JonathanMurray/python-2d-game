#!/usr/bin/env python3
from pythongame.core.game_data import CONSUMABLES, \
    get_consumables_with_level
from pythongame.core.item_data import get_items_with_level, get_item_data_by_type, create_item_description, \
    randomized_item_id
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
            print("{:<25}".format(c_type.name) + "{:<15}".format("") + str(CONSUMABLES[c_type].description))
        for i_type in item_types:
            data = get_item_data_by_type(i_type)
            description_lines = [line.text for line in create_item_description(randomized_item_id(i_type))]
            print("{:<25}".format(data.base_name) + "{:<15}".format("(unique)" if data.is_unique else "") + ", ".join(
                description_lines))
        print("")


register_all_game_data()
print_loot()
