from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item, \
    register_randomized_stat_modifying_item


def register_royal_sword_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ROYAL_SWORD,
        ui_icon_sprite=UiIconSprite.ITEM_ROYAL_SWORD,
        sprite=Sprite.ITEM_ROYAL_SWORD,
        image_file_path="resources/graphics/item_royal_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Royal Sword",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: [0.14, 0.15, 0.16], HeroStat.ARMOR: [1]}
    )
