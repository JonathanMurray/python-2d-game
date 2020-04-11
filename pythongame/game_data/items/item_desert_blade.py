from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_data import interval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_desert_blade_item():
    register_randomized_stat_modifying_item(
        item_level=7,
        item_type=ItemType.DESERT_BLADE,
        ui_icon_sprite=UiIconSprite.ITEM_DESERT_BLADE,
        sprite=Sprite.ITEM_DESERT_BLADE,
        image_file_path="resources/graphics/item_desert_blade.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Desert blade",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: interval(0.4, 0.45, 0.01),
                                 HeroStat.DODGE_CHANCE: interval(0.03, 0.06, 0.01)}
    )
