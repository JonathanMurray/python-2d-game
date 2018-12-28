from pythongame.core.common import PotionType, Sprite
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, UiIconSprite, register_potion_data, PotionData, POTION_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.potion_effects import create_potion_visual_effect_at_player, PotionWasConsumed, \
    PotionFailedToBeConsumed, \
    register_potion_effect
from pythongame.core.visual_effects import create_visual_healing_text

HEALING_AMOUNT = 50


def _apply_health(game_state: GameState):
    player_state = game_state.player_state
    if game_state.player_state.health < game_state.player_state.max_health:
        create_potion_visual_effect_at_player(game_state)
        game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, HEALING_AMOUNT))
        player_state.gain_health(HEALING_AMOUNT)
        return PotionWasConsumed()
    else:
        return PotionFailedToBeConsumed("Already at full health!")


def register_health_potion():
    potion_type = PotionType.HEALTH
    sprite = Sprite.POTION_HEALTH
    ui_icon_sprite = UiIconSprite.POTION_HEALTH

    register_potion_effect(potion_type, _apply_health)
    image_path = "resources/graphics/icon_potion_health.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Restores " + str(HEALING_AMOUNT) + " health"
    register_potion_data(potion_type, PotionData(ui_icon_sprite, sprite, "Health potion", description))
