from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, StatModifierInterval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_leather_armor_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.LEATHER_ARMOR,
        item_level=1,
        ui_icon_sprite=UiIconSprite.ITEM_LEATHER_ARMOR,
        sprite=Sprite.ITEM_LEATHER_ARMOR,
        image_file_path="resources/graphics/item_leather_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Leather armor",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [1])]
    )
