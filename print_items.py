#!/usr/bin/env python3
from pythongame.core.common import item_type_from_id
from pythongame.core.game_data import get_items_with_category, get_optional_item_level
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.register_game_data import register_all_game_data


def print_items():
    for category in [c for c in ItemEquipmentCategory] + [None]:
        if category:
            print(category.name + ":")
        else:
            print("PASSIVE:")
        print("- - - - -")
        entries = [(i_id, i_data, get_optional_item_level(item_type_from_id(i_id)))
                   for (i_id, i_data) in get_items_with_category(category)]
        entries.sort(key=lambda entry: entry[2] if entry[2] else 9999)
        for item_id, item_data, item_level in entries:
            level_text = "level {:<10}".format(item_level) if item_level else " " * 16
            print("{:<25}".format(item_id) + level_text + str(item_data.description_lines))
        print("")


register_all_game_data()
print_items()
