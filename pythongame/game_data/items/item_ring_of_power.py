from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_ring_of_power_item():
    register_stat_modifying_item(
        item_type=ItemType.RING_OF_POWER,
        ui_icon_sprite=UiIconSprite.ITEM_RING_OF_POWER,
        sprite=Sprite.ITEM_RING_OF_POWER,
        image_file_path="resources/graphics/item_ring_of_power.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="Ring of Power",
        stat_modifiers={HeroStat.DAMAGE: 0.1}
    )
