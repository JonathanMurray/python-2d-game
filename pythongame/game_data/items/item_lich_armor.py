from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_lich_armor_item():
    register_stat_modifying_item(
        item_type=ItemType.LICH_ARMOR,
        ui_icon_sprite=UiIconSprite.ITEM_LICH_ARMOR,
        sprite=Sprite.ITEM_LICH_ARMOR,
        image_file_path="resources/graphics/item_lich_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Lich Armor",
        stat_modifiers={HeroStat.MAX_MANA: 40}
    )
