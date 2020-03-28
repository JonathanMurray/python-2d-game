from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_soldiers_helmet_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.SOLDIERS_HELMET,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_SOLDIERS_HELMET,
        sprite=Sprite.ITEM_SOLDIERS_HELMET,
        image_file_path="resources/graphics/item_soldiers_helmet.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Soldier helmet",
        stat_modifier_intervals={HeroStat.ARMOR: [2]}
    )
