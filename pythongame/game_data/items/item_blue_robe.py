from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_blue_robe_item():
    item_types = [ItemType.BLUE_ROBE_1, ItemType.BLUE_ROBE_2, ItemType.BLUE_ROBE_3]
    mana_amounts = [10, 15, 20]
    mana_regen_boost = 0.5
    ui_icon_sprite = UiIconSprite.ITEM_BLUE_ROBE
    sprite = Sprite.ITEM_BLUE_ROBE
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blue_robe.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blue_robe.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]
        mana_amount = mana_amounts[i]
        effect = StatModifyingItemEffect(item_type, {
            HeroStat.MANA_REGEN: mana_regen_boost,
            HeroStat.MAX_MANA: mana_amount
        })
        register_item_effect(item_type, effect)
        name = "Blue Robe (" + str(i + 1) + ")"
        description = effect.get_description()
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.CHEST)
        register_item_data(item_type, item_data)
