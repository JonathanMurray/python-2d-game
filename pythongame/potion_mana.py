from pythongame.core.common import PotionType
from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite, register_potion_icon_sprite
from pythongame.core.game_state import GameState
from pythongame.core.potions import create_potion_visual_effect_at_player, PotionWasConsumed, PotionFailedToBeConsumed, \
    register_potion_effect
from pythongame.core.visual_effects import create_visual_mana_text


def _apply_mana(game_state: GameState):
    player_state = game_state.player_state
    if game_state.player_state.mana < game_state.player_state.max_mana:
        create_potion_visual_effect_at_player(game_state)
        mana_amount = 25
        player_state.gain_mana(mana_amount)
        game_state.visual_effects.append(create_visual_mana_text(game_state.player_entity, mana_amount))
        return PotionWasConsumed()
    else:
        return PotionFailedToBeConsumed("Already at full mana!")


def register_mana_potion():
    register_potion_effect(PotionType.MANA, _apply_mana)
    register_potion_icon_sprite(PotionType.MANA, UiIconSprite.MANA_POTION)
    register_ui_icon_sprite_path(UiIconSprite.MANA_POTION, "resources/graphics/ui_mana_potion.png")
