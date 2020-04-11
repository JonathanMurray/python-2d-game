from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_data import interval
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
        name="Wooden sword",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: interval(0.06, 0.1, 0.01)}
    )
