from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_skull_staff_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.SKULL_STAFF,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_SKULL_STAFF,
        sprite=Sprite.ITEM_SKULL_STAFF,
        image_file_path="resources/graphics/item_skullstaff.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Skull staff",
        stat_modifier_intervals={HeroStat.DAMAGE: interval(0.08, 0.14, 0.01),
                                 HeroStat.LIFE_STEAL: interval(0.07, 0.1, 0.01)}
    )
