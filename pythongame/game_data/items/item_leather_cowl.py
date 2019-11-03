from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_leather_cowl_item():
    item_type = ItemType.LEATHER_COWL
    armor_boost = 1
    ui_icon_sprite = UiIconSprite.ITEM_LEATHER_COWL
    sprite = Sprite.ITEM_LEATHER_COWL
    effect = StatModifyingItemEffect(item_type, {HeroStat.ARMOR: armor_boost})
    register_item_effect(item_type, effect)
    image_file_path = "resources/graphics/item_leather_cowl.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = effect.get_description()
    item_data = ItemData(ui_icon_sprite, sprite, "Leather cowl", description, ItemEquipmentCategory.HEAD)
    register_item_data(item_type, item_data)
