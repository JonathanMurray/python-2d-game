from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_elite_helmet_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ELITE_HELMET,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_ELITE_HELMET,
        sprite=Sprite.ITEM_ELITE_HELMET,
        image_file_path="resources/graphics/item_elite_helmet.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Elite helmet",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [3])]
    )
