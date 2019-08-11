from pythongame.core.common import ConsumableType, Sprite, UiIconSprite
from pythongame.core.consumable_effects import ConsumableFailedToBeConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory
from pythongame.core.game_state import GameState


def _apply(_: GameState):
    return ConsumableFailedToBeConsumed("Not implemented yet!")


def register_warpstone_consumable():
    consumable_type = ConsumableType.WARP_STONE
    sprite = Sprite.CONSUMABLE_WARPSTONE
    ui_icon_sprite = UiIconSprite.CONSUMABLE_WARPSTONE

    register_consumable_effect(consumable_type, _apply)
    image_path = "resources/graphics/consumable_warpstone.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Warps you back to safety"
    data = ConsumableData(ui_icon_sprite, sprite, "Warpstone", description, ConsumableCategory.OTHER)
    register_consumable_data(consumable_type, data)
