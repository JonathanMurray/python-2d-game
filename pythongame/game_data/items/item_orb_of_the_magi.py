from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_orb_of_the_magi_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ORB_OF_THE_MAGI,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ORB_OF_THE_MAGI,
        sprite=Sprite.ITEM_ORB_OF_THE_MAGI,
        image_file_path="resources/graphics/item_orb_of_the_magi.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Spell orb",
        stat_modifier_intervals={HeroStat.MAGIC_DAMAGE: [0.1, 0.11, 0.12, 0.13, 0.14, 0.15]}
    )
