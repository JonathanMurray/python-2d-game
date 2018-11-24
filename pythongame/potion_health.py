from pythongame.core.common import PotionType, Sprite
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, UiIconSprite, register_potion_icon_sprite
from pythongame.core.game_state import GameState
from pythongame.core.potions import create_potion_visual_effect_at_player, PotionWasConsumed, PotionFailedToBeConsumed, \
    register_potion_effect
from pythongame.core.visual_effects import create_visual_healing_text

POTION_ENTITY_SIZE = (30, 30)


def _apply_health(game_state: GameState):
    player_state = game_state.player_state
    if game_state.player_state.health < game_state.player_state.max_health:
        create_potion_visual_effect_at_player(game_state)
        healing_amount = 100
        game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, healing_amount))
        player_state.gain_health(healing_amount)
        return PotionWasConsumed()
    else:
        return PotionFailedToBeConsumed("Already at full health!")


def register_health_potion():
    register_potion_effect(PotionType.HEALTH, _apply_health)
    register_entity_sprite_initializer(
        Sprite.HEALTH_POTION, SpriteInitializer("resources/graphics/ui_health_potion.png", POTION_ENTITY_SIZE))
    register_potion_icon_sprite(PotionType.HEALTH, UiIconSprite.HEALTH_POTION)
    register_ui_icon_sprite_path(UiIconSprite.HEALTH_POTION, "resources/graphics/ui_health_potion.png")