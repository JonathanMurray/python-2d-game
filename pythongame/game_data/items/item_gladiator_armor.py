from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_gladiator_armor():
    item_type = ItemType.GLADIATOR_ARMOR
    max_health_boost = 15
    armor_boost = 2
    damage_boost = 0.05
    ui_icon_sprite = UiIconSprite.ITEM_GLADIATOR_ARMOR
    sprite = Sprite.ITEM_GLADIATOR_ARMOR
    image_file_path = "resources/graphics/item_gladiator_armor.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    effect = StatModifyingItemEffect(item_type, {
        HeroStat.MAX_HEALTH: max_health_boost,
        HeroStat.ARMOR: armor_boost,
        HeroStat.DAMAGE: damage_boost
    })
    register_item_effect(item_type, effect)
    name = "Gladiator's armor"
    description = [str(armor_boost) + " armor",
                   "+" + str(max_health_boost) + " max health",
                   "+" + str(int(round(damage_boost * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.CHEST)
    register_item_data(item_type, item_data)
