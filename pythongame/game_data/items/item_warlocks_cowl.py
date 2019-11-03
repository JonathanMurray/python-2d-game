from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_warlocks_cowl_item():
    register_stat_modifying_item(
        item_type=ItemType.WARLOCKS_COWL,
        ui_icon_sprite=UiIconSprite.ITEM_WARLOCKS_COWL,
        sprite=Sprite.ITEM_WARLOCKS_COWL,
        image_file_path="resources/graphics/item_warlocks_cowl.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Warlock's Cowl",
        stat_modifiers={HeroStat.LIFE_STEAL: 0.1}
    )
