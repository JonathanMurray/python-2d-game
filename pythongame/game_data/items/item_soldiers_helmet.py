from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_soldiers_helmet_item():
    item_types = [ItemType.SOLDIERS_HELMET_1, ItemType.SOLDIERS_HELMET_2, ItemType.SOLDIERS_HELMET_3]
    health_amounts = [10, 15, 20]
    armor_boost = 2
    ui_icon_sprite = UiIconSprite.ITEM_SOLDIERS_HELMET
    sprite = Sprite.ITEM_SOLDIERS_HELMET
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_soldiers_helmet.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_soldiers_helmet.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]
        health_amount = health_amounts[i]
        effect = StatModifyingItemEffect(item_type, {HeroStat.ARMOR: armor_boost, HeroStat.MAX_HEALTH: health_amount})
        register_item_effect(item_type, effect)
        name = "Soldier's Helmet (" + str(i + 1) + ")"
        description = [str(armor_boost) + " armor",
                       "+" + str(health_amount) + " max health"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.HEAD)
        register_item_data(item_type, item_data)
