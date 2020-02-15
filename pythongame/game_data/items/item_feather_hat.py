from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_feather_hat_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.FEATHER_HAT,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_FEATHER_HAT,
        sprite=Sprite.ITEM_FEATHER_HAT,
        image_file_path="resources/graphics/item_feather_hat.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Feather hat",
        stat_modifier_intervals={HeroStat.HEALTH_REGEN: [0.1, 0.2, 0.3], HeroStat.MANA_REGEN: [0.1, 0.2, 0.3]}
    )
