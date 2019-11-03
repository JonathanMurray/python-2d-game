from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_knights_armor():
    item_type = ItemType.KNIGHTS_ARMOR
    armor_boost = 2
    speed_decrease = 0.05
    ui_icon_sprite = UiIconSprite.ITEM_KNIGHTS_ARMOR
    sprite = Sprite.ITEM_KNIGHTS_ARMOR
    image_file_path = "resources/graphics/item_knights_armor.png"
    effect = StatModifyingItemEffect(item_type, {HeroStat.ARMOR: armor_boost, HeroStat.MOVEMENT_SPEED: -speed_decrease})
    register_item_effect(item_type, effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = [str(armor_boost) + " armor",
                   "Reduces movement speed by {:.0f}".format(speed_decrease * 100) + "%"]
    item_data = ItemData(ui_icon_sprite, sprite, "Knight's Armor", description, ItemEquipmentCategory.CHEST)
    register_item_data(item_type, item_data)
