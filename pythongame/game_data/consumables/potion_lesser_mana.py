from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, SoundId
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed, register_consumable_effect
from pythongame.core.damage_interactions import player_receive_mana
from pythongame.core.game_data import POTION_ENTITY_SIZE, ConsumableCategory, register_consumable_level
from pythongame.core.game_data import register_ui_icon_sprite_path, register_entity_sprite_initializer, \
    register_consumable_data, ConsumableData
from pythongame.core.game_state import GameState
from pythongame.core.view.image_loading import SpriteInitializer

MANA_AMOUNT = 40


def _apply_mana(game_state: GameState):
    if not game_state.player_state.mana_resource.is_at_max():
        create_potion_visual_effect_at_player(game_state)
        player_receive_mana(MANA_AMOUNT, game_state)
        return ConsumableWasConsumed()
    else:
        return ConsumableFailedToBeConsumed("Already at full mana!")


def register_lesser_mana_potion():
    consumable_type = ConsumableType.MANA_LESSER
    sprite = Sprite.POTION_MANA_LESSER
    ui_icon_sprite = UiIconSprite.POTION_MANA_LESSER
    register_consumable_level(consumable_type, 2)
    register_consumable_effect(consumable_type, _apply_mana)
    image_path = "resources/graphics/icon_potion_lesser_mana.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    data = ConsumableData(ui_icon_sprite, sprite, "Lesser mana potion", "Restores " + str(MANA_AMOUNT) + " mana",
                          ConsumableCategory.MANA, SoundId.CONSUMABLE_POTION)
    register_consumable_data(consumable_type, data)
