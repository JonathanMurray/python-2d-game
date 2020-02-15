from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_thiefs_mask_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.THIEFS_MASK,
        ui_icon_sprite=UiIconSprite.ITEM_THIEFS_MASK,
        sprite=Sprite.ITEM_THIEFS_MASK,
        image_file_path="resources/graphics/item_thiefs_mask.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Thief's mask",
        stat_modifier_intervals={HeroStat.DODGE_CHANCE: [0.1],
                                 HeroStat.DAMAGE: [0.05],
                                 HeroStat.MANA_REGEN: [0.03]},
        is_unique=True
    )
