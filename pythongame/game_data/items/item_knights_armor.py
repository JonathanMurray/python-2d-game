from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_knights_armor():
    register_randomized_stat_modifying_item(
        item_type=ItemType.KNIGHTS_ARMOR,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_KNIGHTS_ARMOR,
        sprite=Sprite.ITEM_KNIGHTS_ARMOR,
        image_file_path="resources/graphics/item_knights_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Knight armor",
        stat_modifier_intervals={HeroStat.ARMOR: [2]}
    )
