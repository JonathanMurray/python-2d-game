from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_wand_item():
    item_type = ItemType.WAND
    mana_regen_bonus = 0.3
    max_mana_bonus = 10
    ui_icon_sprite = UiIconSprite.ITEM_WAND
    sprite = Sprite.ITEM_WAND
    image_file_path = "resources/graphics/item_wand.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(
        sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    effect = StatModifyingItemEffect(item_type, {
        HeroStat.MANA_REGEN: mana_regen_bonus,
        HeroStat.MAX_MANA: max_mana_bonus
    })
    register_item_effect(item_type, effect)
    name = "Wizard's wand"
    description = ["+" + str(mana_regen_bonus) + " mana regen",
                   "+" + str(max_mana_bonus) + " max mana"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(item_type, item_data)
