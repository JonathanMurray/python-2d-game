from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_wooden_sword_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.WOODEN_SWORD,
        item_level=1,
        ui_icon_sprite=UiIconSprite.ITEM_WOODEN_SWORD,
        sprite=Sprite.ITEM_WOODEN_SWORD,
        image_file_path="resources/graphics/item_wooden_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Wooden Sword",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: [0.04, 0.05, 0.06]}
    )
