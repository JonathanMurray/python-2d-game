from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_practice_sword_item():
    register_stat_modifying_item(
        item_type=ItemType.PRACTICE_SWORD,
        ui_icon_sprite=UiIconSprite.ITEM_PRACTICE_SWORD,
        sprite=Sprite.ITEM_PRACTICE_SWORD,
        image_file_path="resources/graphics/item_practice_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Practice Sword",
        stat_modifiers={HeroStat.PHYSICAL_DAMAGE: 0.03}
    )
