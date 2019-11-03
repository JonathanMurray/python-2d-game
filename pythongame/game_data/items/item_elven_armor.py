from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_elven_armor():
    item_type = ItemType.ELVEN_ARMOR
    mana_regen_boost = 0.5
    mana_boost = 15
    armor_boost = 1
    ui_icon_sprite = UiIconSprite.ITEM_ELVEN_ARMOR
    sprite = Sprite.ITEM_ELVEN_ARMOR
    image_file_path = "resources/graphics/item_elven_armor.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    effect = StatModifyingItemEffect(item_type, {
        HeroStat.MANA_REGEN: mana_regen_boost,
        HeroStat.MAX_MANA: mana_boost,
        HeroStat.ARMOR: armor_boost
    })
    register_item_effect(item_type, effect)
    name = "Elven Armor"
    description = [str(armor_boost) + " armor",
                   "+" + str(mana_regen_boost) + " mana regen",
                   "+" + str(mana_boost) + " max mana"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.CHEST)
    register_item_data(item_type, item_data)
