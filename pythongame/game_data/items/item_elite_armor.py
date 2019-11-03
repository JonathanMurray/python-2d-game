from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_elite_armor():
    register_stat_modifying_item(
        item_type=ItemType.ELITE_ARMOR,
        ui_icon_sprite=UiIconSprite.ITEM_ELITE_ARMOR,
        sprite=Sprite.ITEM_ELITE_ARMOR,
        image_file_path="resources/graphics/item_elite_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Elite Armor",
        stat_modifiers={HeroStat.HEALTH_REGEN: 0.5, HeroStat.ARMOR: 2}
    )
