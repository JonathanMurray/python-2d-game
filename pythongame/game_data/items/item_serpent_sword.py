from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_serpent_sword_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.SERPENT_SWORD,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_SERPENT_SWORD,
        sprite=Sprite.ITEM_SERPENT_SWORD,
        image_file_path="resources/graphics/item_serpent_sword.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Serpent sword",
        stat_modifier_intervals={HeroStat.DAMAGE: [0.18, 0.19, 0.20, 0.21, 0.22],
                                 HeroStat.MANA_REGEN: [0.3, 0.4, 0.5, 0.6]}
    )
