from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_amulet_of_mana_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.AMULET_OF_MANA,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_AMULET_OF_MANA,
        sprite=Sprite.ITEM_AMULET_OF_MANA,
        image_file_path="resources/graphics/item_amulet.png",
        item_equipment_category=ItemEquipmentCategory.NECK,
        name="Arcane necklace",
        stat_modifier_intervals={HeroStat.MANA_REGEN: [0.4, 0.5, 0.6, 0.7, 0.8]}
    )
