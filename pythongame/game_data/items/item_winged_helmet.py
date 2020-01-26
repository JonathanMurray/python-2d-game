from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_winged_helmet_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.WINGED_HELMET,
        ui_icon_sprite=UiIconSprite.ITEM_WINGED_HELMET,
        sprite=Sprite.ITEM_WINGED_HELMET,
        image_file_path="resources/graphics/item_winged_helmet.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Winged helmet",
        stat_modifier_intervals={HeroStat.ARMOR: [3], HeroStat.MOVEMENT_SPEED: [0.18, 0.19, 0.20]}
    )
