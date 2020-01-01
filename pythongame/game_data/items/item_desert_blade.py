from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_desert_blade_item():
    register_stat_modifying_item(
        item_type=ItemType.DESERT_BLADE,
        ui_icon_sprite=UiIconSprite.ITEM_DESERT_BLADE,
        sprite=Sprite.ITEM_DESERT_BLADE,
        image_file_path="resources/graphics/item_desert_blade.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Desert Blade",
        stat_modifiers={HeroStat.PHYSICAL_DAMAGE: 0.15, HeroStat.DODGE_CHANCE: 0.05, HeroStat.LIFE_STEAL: 0.05}
    )
