from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, SoundId
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed, \
    register_consumable_effect
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import register_entity_sprite_initializer, register_ui_icon_sprite_path, \
    register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory, register_consumable_level
from pythongame.core.game_state import GameState
from pythongame.core.view.image_loading import SpriteInitializer

HEALING_AMOUNT = 40


def _apply_health(game_state: GameState):
    if not game_state.player_state.health_resource.is_at_max():
        create_potion_visual_effect_at_player(game_state)
        player_receive_healing(HEALING_AMOUNT, game_state)
        return ConsumableWasConsumed()
    else:
        return ConsumableFailedToBeConsumed("Already at full health!")


def register_lesser_health_potion():
    consumable_type = ConsumableType.HEALTH_LESSER
    sprite = Sprite.POTION_HEALTH_LESSER
    ui_icon_sprite = UiIconSprite.POTION_HEALTH_LESSER
    register_consumable_level(consumable_type, 2)
    register_consumable_effect(consumable_type, _apply_health)
    image_path = "resources/graphics/icon_potion_lesser_health.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Restores " + str(HEALING_AMOUNT) + " health"
    data = ConsumableData(ui_icon_sprite, sprite, "Lesser health potion", description, ConsumableCategory.HEALTH,
                          SoundId.CONSUMABLE_POTION)
    register_consumable_data(consumable_type, data)
