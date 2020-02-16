from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_bronze_ring_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.BRONZE_RING,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_BRONZE_RING,
        sprite=Sprite.ITEM_BRONZE_RING,
        image_file_path="resources/graphics/item_bronze_ring.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="Bronze ring",
        stat_modifier_intervals={HeroStat.MAX_MANA: [8, 9, 10, 11, 12]}
    )
