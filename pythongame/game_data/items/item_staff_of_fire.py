from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_staff_of_fire_item():
    item_type = ItemType.STAFF_OF_FIRE
    register_stat_modifying_item(
        item_type=item_type,
        ui_icon_sprite=UiIconSprite.ITEM_STAFF_OF_FIRE,
        sprite=Sprite.ITEM_STAFF_OF_FIRE,
        image_file_path="resources/graphics/item_staff_of_fire.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Staff of Fire",
        stat_modifiers={HeroStat.MAGIC_DAMAGE: 0.3}
    )
