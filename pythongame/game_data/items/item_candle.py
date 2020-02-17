from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_candle_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.CANDLE,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_CANDLE,
        sprite=Sprite.ITEM_CANDLE,
        image_file_path="resources/graphics/item_candle.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Candle",
        stat_modifier_intervals={HeroStat.MAGIC_RESIST_CHANCE: [0.14, 0.15, 0.16, 0.17]}
    )
