from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_novice_wand_item():
    register_stat_modifying_item(
        item_type=ItemType.NOVICE_WAND,
        ui_icon_sprite=UiIconSprite.ITEM_NOVICE_WAND,
        sprite=Sprite.ITEM_NOVICE_WAND,
        image_file_path="resources/graphics/item_novice_wand.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Novice wand",
        stat_modifiers={HeroStat.MANA_REGEN: 0.25}
    )
