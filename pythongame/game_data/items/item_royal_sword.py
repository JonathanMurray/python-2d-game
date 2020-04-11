from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, StatModifierInterval
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_royal_sword_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ROYAL_SWORD,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_ROYAL_SWORD,
        sprite=Sprite.ITEM_ROYAL_SWORD,
        image_file_path="resources/graphics/item_royal_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Royal sword",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.25, 0.35, 0.01)),
                                 StatModifierInterval(HeroStat.ARMOR, [1])]
    )
