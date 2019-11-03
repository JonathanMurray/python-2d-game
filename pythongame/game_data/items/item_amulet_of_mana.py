from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_amulet_of_mana_item():
    item_types = [ItemType.AMULET_OF_MANA_1, ItemType.AMULET_OF_MANA_2, ItemType.AMULET_OF_MANA_3]
    mana_regen_boosts = [0.5, 0.75, 1]
    ui_icon_sprite = UiIconSprite.ITEM_AMULET_OF_MANA
    sprite = Sprite.ITEM_AMULET_OF_MANA
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_amulet.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_amulet.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]
        mana_regen_boost = mana_regen_boosts[i]
        effect = StatModifyingItemEffect(item_type, {HeroStat.MANA_REGEN: mana_regen_boost})
        register_item_effect(item_type, effect)
        name = "Amulet of Mana (" + str(i + 1) + ")"
        description = ["+" + str(mana_regen_boost) + " mana regen"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.NECK)
        register_item_data(item_type, item_data)
