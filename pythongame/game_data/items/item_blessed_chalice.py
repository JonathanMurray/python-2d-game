from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_blessed_chalice_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.BLESSED_CHALICE,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_BLESSED_CHALICE,
        sprite=Sprite.ITEM_BLESSED_CHALICE,
        image_file_path="resources/graphics/item_blessed_chalice.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Chalice",
        stat_modifier_intervals={HeroStat.HEALTH_REGEN: [1, 1.2, 1.4, 1.6, 1.8, 2]}
    )
