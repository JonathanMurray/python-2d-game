from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_royal_dagger_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ROYAL_DAGGER,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ROYAL_DAGGER,
        sprite=Sprite.ITEM_ROYAL_DAGGER,
        image_file_path="resources/graphics/item_royal_dagger.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Royal Dagger",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: [0.18, 0.19, 0.2]}
    )
