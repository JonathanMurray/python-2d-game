from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_skull_staff_item():
    register_stat_modifying_item(
        item_type=ItemType.SKULL_STAFF,
        ui_icon_sprite=UiIconSprite.ITEM_SKULL_STAFF,
        sprite=Sprite.ITEM_SKULL_STAFF,
        image_file_path="resources/graphics/item_skullstaff.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Skull Staff",
        stat_modifiers={HeroStat.LIFE_STEAL: 0.1}
    )
