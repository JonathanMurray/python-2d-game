from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat, StatModifierInterval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_lich_armor_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.LICH_ARMOR,
        item_level=7,
        ui_icon_sprite=UiIconSprite.ITEM_LICH_ARMOR,
        sprite=Sprite.ITEM_LICH_ARMOR,
        image_file_path="resources/graphics/item_lich_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Lich armor",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [1]),
                                 StatModifierInterval(HeroStat.MAX_MANA, [40]),
                                 StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, [0.05])],
        is_unique=True
    )
