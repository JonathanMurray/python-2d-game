from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_ring_of_power_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.RING_OF_POWER,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_RING_OF_POWER,
        sprite=Sprite.ITEM_RING_OF_POWER,
        image_file_path="resources/graphics/item_ring_of_power.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="Force ring",
        stat_modifier_intervals={HeroStat.DAMAGE: interval(0.1, 0.2, 0.01)}
    )
