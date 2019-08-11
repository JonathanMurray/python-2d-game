from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect
from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, BuffType, Millis
from pythongame.core.consumable_effects import register_consumable_effect, ConsumableWasConsumed
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory
from pythongame.core.game_state import GameState


def _apply(game_state: GameState):
    teleport_buff_effect: AbstractBuffEffect = get_buff_effect(
        BuffType.BEING_TELEPORTED, game_state.player_spawn_position)
    delay = Millis(600)
    game_state.player_state.gain_buff_effect(teleport_buff_effect, delay)
    return ConsumableWasConsumed()


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
