from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_orb_of_life_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ORB_OF_LIFE,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ORB_OF_LIFE,
        sprite=Sprite.ITEM_ORB_OF_LIFE,
        image_file_path="resources/graphics/item_orb_of_life.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Nature orb",
        stat_modifier_intervals={HeroStat.LIFE_STEAL: [0.04, 0.05, 0.06, 0.07, 0.08]}
    )
