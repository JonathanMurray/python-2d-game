from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_gladiator_armor():
    register_randomized_stat_modifying_item(
        item_type=ItemType.GLADIATOR_ARMOR,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_GLADIATOR_ARMOR,
        sprite=Sprite.ITEM_GLADIATOR_ARMOR,
        image_file_path="resources/graphics/item_gladiator_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Gladiator's armor",
        stat_modifier_intervals={HeroStat.ARMOR: [2], HeroStat.DAMAGE: [0.03, 0.04, 0.05]}
    )
