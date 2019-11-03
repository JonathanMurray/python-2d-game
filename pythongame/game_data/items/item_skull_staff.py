from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_skull_staff_item():
    item_type = ItemType.SKULL_STAFF
    life_steal_boost = 0.1
    ui_icon_sprite = UiIconSprite.ITEM_SKULL_STAFF
    sprite = Sprite.ITEM_SKULL_STAFF
    effect = StatModifyingItemEffect(item_type, {HeroStat.LIFE_STEAL: life_steal_boost})
    register_item_effect(item_type, effect)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_skullstaff.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_skullstaff.png", ITEM_ENTITY_SIZE))
    description = effect.get_description()
    item_data = ItemData(ui_icon_sprite, sprite, "Skull Staff", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(item_type, item_data)
