from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_noble_defender():
    item_type = ItemType.NOBLE_DEFENDER
    register_randomized_stat_modifying_item(
        item_type=item_type,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_NOBLE_DEFENDER,
        sprite=Sprite.ITEM_NOBLE_DEFENDER,
        image_file_path="resources/graphics/item_noble_defender.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Lion shield",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [4]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [8, 9, 10]),
                                 StatModifierInterval(HeroStat.BLOCK_CHANCE, [0.04, 0.05])]
    )
