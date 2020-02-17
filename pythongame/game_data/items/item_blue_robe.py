from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_blue_robe_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.BLUE_ROBE,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_BLUE_ROBE,
        sprite=Sprite.ITEM_BLUE_ROBE,
        image_file_path="resources/graphics/item_blue_robe.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Blue robe",
        stat_modifier_intervals={HeroStat.MANA_REGEN: [0.3, 0.4, 0.5]}
    )
