from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_orb_of_wisdom_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ORB_OF_WISDOM,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ORB_OF_WISDOM,
        sprite=Sprite.ITEM_ORB_OF_WISDOM,
        image_file_path="resources/graphics/item_orb_of_wisdom.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Arcane orb",
        stat_modifier_intervals={HeroStat.MANA_REGEN: [0.5, 0.6, 0.7, 0.8, 0.9, 1]}
    )
