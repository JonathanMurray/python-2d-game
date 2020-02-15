from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, StatModifierInterval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_wooden_shield():
    register_randomized_stat_modifying_item(
        item_type=ItemType.WOODEN_SHIELD,
        item_level=1,
        ui_icon_sprite=UiIconSprite.ITEM_WOODEN_SHIELD,
        sprite=Sprite.ITEM_WOODEN_SHIELD,
        image_file_path="resources/graphics/item_wooden_shield.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Wooden shield",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [1]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [3])]
    )
