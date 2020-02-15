from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_elite_armor():
    register_randomized_stat_modifying_item(
        item_type=ItemType.ELITE_ARMOR,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_ELITE_ARMOR,
        sprite=Sprite.ITEM_ELITE_ARMOR,
        image_file_path="resources/graphics/item_elite_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Elite armor",
        stat_modifier_intervals={HeroStat.ARMOR: [3]}
    )
