from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_leather_cowl_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.LEATHER_COWL,
        item_level=2,
        ui_icon_sprite=UiIconSprite.ITEM_LEATHER_COWL,
        sprite=Sprite.ITEM_LEATHER_COWL,
        image_file_path="resources/graphics/item_leather_cowl.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Leather cowl",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [1])]
    )
