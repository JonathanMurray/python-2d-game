from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_knights_armor():
    register_stat_modifying_item(
        item_type=ItemType.KNIGHTS_ARMOR,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_KNIGHTS_ARMOR,
        sprite=Sprite.ITEM_KNIGHTS_ARMOR,
        image_file_path="resources/graphics/item_knights_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Knight's Armor",
        stat_modifiers={HeroStat.ARMOR: 2}
    )
