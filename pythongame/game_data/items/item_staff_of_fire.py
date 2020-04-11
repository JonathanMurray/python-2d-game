from pythongame.core.common import HeroStat, StatModifierInterval
from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_randomized_stat_modifying_item


def register_staff_of_fire_item():
    register_randomized_stat_modifying_item(
        item_type=ItemType.STAFF_OF_FIRE,
        ui_icon_sprite=UiIconSprite.ITEM_STAFF_OF_FIRE,
        sprite=Sprite.ITEM_STAFF_OF_FIRE,
        image_file_path="resources/graphics/item_staff_of_fire.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Staff of the Phoenix",
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MAGIC_DAMAGE, [0.25]),
                                 StatModifierInterval(HeroStat.MAX_MANA, [10]),
                                 StatModifierInterval(HeroStat.LIFE_ON_KILL, [1])],
        is_unique=True
    )
