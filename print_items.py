#!/usr/bin/env python3

from pythongame.core.game_data import get_items_with_category
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.register_game_data import register_all_game_data


def print_items():
    for category in [c for c in ItemEquipmentCategory] + [None]:
        if category:
            print(category.name + ":")
        else:
            print("PASSIVE:")
        print("- - - - -")
        for item_id, item_data in get_items_with_category(category):
            print("{:<25}".format(item_id) + str(item_data.description_lines))
        print("")


register_all_game_data()
print_items()
