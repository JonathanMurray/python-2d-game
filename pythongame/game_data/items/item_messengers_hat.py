from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_messengers_hat_item():
    item_type = ItemType.MESSENGERS_HAT
    speed_multiplier = 0.2
    ui_icon_sprite = UiIconSprite.ITEM_MESSENGERS_HAT
    sprite = Sprite.ITEM_MESSENGERS_HAT
    register_item_effect(item_type, StatModifyingItemEffect(item_type, {HeroStat.MOVEMENT_SPEED: speed_multiplier}))
    image_file_path = "resources/graphics/item_messengers_hat.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["Increases movement speed by " + str(int(speed_multiplier * 100)) + "%"]
    item_data = ItemData(ui_icon_sprite, sprite, "Messenger's hat", description, ItemEquipmentCategory.HEAD)
    register_item_data(item_type, item_data)
