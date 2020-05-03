from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_skull_sword_item():
    item_type = ItemType.SKULL_SWORD
    register_randomized_stat_modifying_item(
        item_type=item_type,
        item_level=8,
        ui_icon_sprite=UiIconSprite.ITEM_SKULL_SWORD,
        sprite=Sprite.ITEM_SKULL_SWORD,
        image_file_path="resources/graphics/item_skull_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Skull sword",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, interval(0.4, 0.5, 0.01)),
                                 StatModifierInterval(HeroStat.LIFE_STEAL, interval(0.10, 0.15, 0.01))]
    )
