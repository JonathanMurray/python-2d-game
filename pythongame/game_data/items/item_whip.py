from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_whip_item():
    register_stat_modifying_item(
        item_type=ItemType.WHIP,
        ui_icon_sprite=UiIconSprite.ITEM_WHIP,
        sprite=Sprite.ITEM_WHIP,
        image_file_path="resources/graphics/item_whip.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Whip",
        stat_modifiers={HeroStat.PHYSICAL_DAMAGE: 0.05, HeroStat.LIFE_STEAL: 0.05, HeroStat.MOVEMENT_SPEED: 0.05}
    )
