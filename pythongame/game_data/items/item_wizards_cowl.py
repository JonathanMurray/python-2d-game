from pythongame.core.common import ItemType, Sprite, StatModifierInterval, HeroStat
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_wizards_cowl():
    item_type = ItemType.WIZARDS_COWL
    register_randomized_stat_modifying_item(
        item_type=item_type,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_WIZARDS_COWL,
        sprite=Sprite.ITEM_WIZARDS_COWL,
        image_file_path="resources/graphics/item_wizards_cowl.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Wizard cowl",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MANA_ON_KILL, [2, 3])],
    )
