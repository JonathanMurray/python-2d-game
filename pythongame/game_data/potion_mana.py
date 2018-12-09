from pythongame.core.common import PotionType, Sprite
from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite, register_potion_icon_sprite, \
    register_entity_sprite_initializer, SpriteInitializer, register_potion_entity_sprite, register_potion_name
from pythongame.core.game_state import GameState
from pythongame.core.potion_effects import create_potion_visual_effect_at_player, PotionWasConsumed, PotionFailedToBeConsumed, \
    register_potion_effect
from pythongame.core.visual_effects import create_visual_mana_text
from pythongame.game_data.potion_health import POTION_ENTITY_SIZE


# TODO Don't depend on potion_health from here

def _apply_mana(game_state: GameState):
    player_state = game_state.player_state
    if game_state.player_state.mana < game_state.player_state.max_mana:
        create_potion_visual_effect_at_player(game_state)
        mana_amount = 50
        player_state.gain_mana(mana_amount)
        game_state.visual_effects.append(create_visual_mana_text(game_state.player_entity, mana_amount))
        return PotionWasConsumed()
    else:
        return PotionFailedToBeConsumed("Already at full mana!")


def register_mana_potion():
    potion_type = PotionType.MANA
    sprite = Sprite.MANA_POTION
    ui_icon_sprite = UiIconSprite.MANA_POTION

    register_potion_effect(potion_type, _apply_mana)
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/ui_mana_potion.png", POTION_ENTITY_SIZE))
    register_potion_icon_sprite(potion_type, ui_icon_sprite)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/ui_mana_potion.png")
    register_potion_entity_sprite(potion_type, sprite)
    register_potion_name(potion_type, "Mana potion")
