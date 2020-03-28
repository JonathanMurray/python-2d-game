from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_druids_ring_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.DRUIDS_RING,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_DRUIDS_RING,
        sprite=Sprite.ITEM_DRUIDS_RING,
        image_file_path="resources/graphics/item_druids_ring.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="Druid ring",
        stat_modifier_intervals={HeroStat.MANA_REGEN: [0.4, 0.5, 0.6, 0.7, 0.8],
                                 HeroStat.HEALTH_REGEN: [0.4, 0.5, 0.6, 0.7, 0.8]}
    )
