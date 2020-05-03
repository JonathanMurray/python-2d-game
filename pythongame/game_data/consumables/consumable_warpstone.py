from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect
from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, BuffType, Direction, SoundId
from pythongame.core.consumable_effects import register_consumable_effect, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed
from pythongame.core.game_data import register_entity_sprite_initializer, register_ui_icon_sprite_path, \
    register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory
from pythongame.core.game_state import GameState
from pythongame.core.math import translate_in_direction
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.game_data.portals import PORTAL_DELAY


def _apply(game_state: GameState):
    if not game_state.is_dungeon:
        # TODO Verify that the destination is clear from collisions
        destination = translate_in_direction(game_state.player_spawn_position, Direction.DOWN, 50)
        teleport_buff_effect: AbstractBuffEffect = get_buff_effect(BuffType.TELEPORTING_WITH_WARP_STONE, destination)
        game_state.player_state.gain_buff_effect(teleport_buff_effect, PORTAL_DELAY)
        return ConsumableWasConsumed()
    else:
        return ConsumableFailedToBeConsumed("Can't warp inside a dungeon!")


def register_warpstone_consumable():
    consumable_type = ConsumableType.WARP_STONE
    sprite = Sprite.CONSUMABLE_WARPSTONE
    ui_icon_sprite = UiIconSprite.CONSUMABLE_WARPSTONE

    register_consumable_effect(consumable_type, _apply)
    image_path = "resources/graphics/consumable_warpstone.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Warps you back to safety"
    data = ConsumableData(ui_icon_sprite, sprite, "Warpstone", description, ConsumableCategory.OTHER, SoundId.WARP)
    register_consumable_data(consumable_type, data)
