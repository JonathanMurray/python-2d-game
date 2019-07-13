from pythongame.core.common import ConsumableType, Sprite, UiIconSprite
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed, register_consumable_effect
from pythongame.core.game_data import POTION_ENTITY_SIZE
from pythongame.core.game_data import register_ui_icon_sprite_path, register_entity_sprite_initializer, \
    SpriteInitializer, register_consumable_data, ConsumableData
from pythongame.core.game_state import GameState
from pythongame.core.visual_effects import create_visual_mana_text

MANA_AMOUNT = 75


def _apply_mana(game_state: GameState):
    player_state = game_state.player_state
    if game_state.player_state.mana < game_state.player_state.max_mana:
        create_potion_visual_effect_at_player(game_state)
        player_state.gain_mana(MANA_AMOUNT)
        game_state.visual_effects.append(create_visual_mana_text(game_state.player_entity, MANA_AMOUNT))
        return ConsumableWasConsumed()
    else:
        return ConsumableFailedToBeConsumed("Already at full mana!")


def register_lesser_mana_potion():
    consumable_type = ConsumableType.MANA_LESSER
    sprite = Sprite.POTION_MANA_LESSER
    ui_icon_sprite = UiIconSprite.POTION_MANA_LESSER

    register_consumable_effect(consumable_type, _apply_mana)
    image_path = "resources/graphics/icon_potion_lesser_mana.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    register_consumable_data(
        consumable_type,
        ConsumableData(ui_icon_sprite, sprite, "Lesser mana potion", "Restores " + str(MANA_AMOUNT) + " mana"))
