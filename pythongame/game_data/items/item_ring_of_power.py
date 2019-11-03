from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_ring_of_power_item():
    item_type = ItemType.RING_OF_POWER
    multiplier_bonus = 0.1
    ui_icon_sprite = UiIconSprite.ITEM_RING_OF_POWER
    sprite = Sprite.ITEM_RING_OF_POWER
    image_file_path = "resources/graphics/item_ring_of_power.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(item_type, StatModifyingItemEffect(item_type, {HeroStat.DAMAGE: multiplier_bonus}))
    name = "Ring of Power"
    description = ["+" + str(int(round(multiplier_bonus * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.RING)
    register_item_data(item_type, item_data)
