from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_fire_gauntlet_item():
    item_type = ItemType.FIRE_GAUNTLET
    register_randomized_stat_modifying_item(
        item_type=item_type,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_FIRE_GAUNTLET,
        sprite=Sprite.ITEM_FIRE_GAUNTLET,
        image_file_path="resources/graphics/item_fire_gauntlet.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Fire gauntlet",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.DAMAGE, interval(0.15, 0.2, 0.01)),
                                 StatModifierInterval(HeroStat.HEALTH_REGEN, interval(0.2, 0.4, 0.1))]
    )
