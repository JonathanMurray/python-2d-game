from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_sun_shield_item():
    item_type = ItemType.SUN_SHIELD
    register_randomized_stat_modifying_item(
        item_type=item_type,
        item_level=8,
        ui_icon_sprite=UiIconSprite.ITEM_SUN_SHIELD,
        sprite=Sprite.ITEM_SUN_SHIELD,
        image_file_path="resources/graphics/item_sun_shield.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Sun shield",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [3]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [15, 16, 17, 18])]
    )
