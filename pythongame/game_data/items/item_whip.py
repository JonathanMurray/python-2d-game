from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_whip_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.WHIP,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_WHIP,
        sprite=Sprite.ITEM_WHIP,
        image_file_path="resources/graphics/item_whip.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Whip",
        stat_modifier_intervals={HeroStat.PHYSICAL_DAMAGE: [0.05, 0.06, 0.07],
                                 HeroStat.LIFE_STEAL: [0.05, 0.06]}
    )
