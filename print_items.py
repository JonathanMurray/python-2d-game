#!/usr/bin/env python3
from typing import Optional

from pythongame.core.game_data import ITEMS
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.register_game_data import register_all_game_data


def items_with_category(category: Optional[ItemEquipmentCategory]):
    return [(item_type, ITEMS[item_type]) for item_type in ITEMS
            if ITEMS[item_type].item_equipment_category == category]


def print_items():
    for category in [c for c in ItemEquipmentCategory] + [None]:
        if category:
            print(category.name + ":")
        else:
            print("PASSIVE:")
        print("- - - - -")
        for item_type, item_data in items_with_category(category):
            print("{:<25}".format(item_type.name) + str(item_data.description_lines))
        print("")


register_all_game_data()
print_items()
