from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_warlords_armor_item():
    register_stat_modifying_item(
        item_type=ItemType.WARLORDS_ARMOR,
        ui_icon_sprite=UiIconSprite.ITEM_WARLORDS_ARMOR,
        sprite=Sprite.ITEM_WARLORDS_ARMOR,
        image_file_path="resources/graphics/item_warlords_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Warlord's Armor",
        stat_modifiers={HeroStat.ARMOR: 4}
    )
