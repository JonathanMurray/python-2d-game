from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_elven_armor():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ELVEN_ARMOR,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ELVEN_ARMOR,
        sprite=Sprite.ITEM_ELVEN_ARMOR,
        image_file_path="resources/graphics/item_elven_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Elven armor",
        stat_modifier_intervals={HeroStat.ARMOR: [1], HeroStat.MANA_REGEN: [0.3, 0.4, 0.5]}
    )
