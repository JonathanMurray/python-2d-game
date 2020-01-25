from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_stat_modifying_item


def register_druids_ring_item():
    register_stat_modifying_item(
        item_type=ItemType.DRUIDS_RING,
        ui_icon_sprite=UiIconSprite.ITEM_DRUIDS_RING,
        sprite=Sprite.ITEM_DRUIDS_RING,
        image_file_path="resources/graphics/item_druids_ring.png",
        item_equipment_category=ItemEquipmentCategory.RING,
        name="Druid's Ring",
        stat_modifiers={HeroStat.MANA_REGEN: 0.5, HeroStat.HEALTH_REGEN: 0.5, HeroStat.MAGIC_RESIST_CHANCE: 0.05}
    )
