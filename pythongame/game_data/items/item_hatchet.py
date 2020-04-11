from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_hatchet_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.HATCHET,
        item_level=2,
        ui_icon_sprite=UiIconSprite.ITEM_HATCHET,
        sprite=Sprite.ITEM_HATCHET,
        image_file_path="resources/graphics/item_hatchet.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Hatchet",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: interval(0.1, 0.15, 0.01)}
    )
