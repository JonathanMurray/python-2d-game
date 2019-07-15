from pythongame.core.ability_learning import player_learn_new_ability
from pythongame.core.common import ConsumableType, Sprite, AbilityType, UiIconSprite
from pythongame.core.consumable_effects import ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ABILITIES, \
    ConsumableCategory
from pythongame.core.game_state import GameState


def _apply(game_state: GameState):
    ability_type = AbilityType.SUMMON
    player_learn_new_ability(game_state.player_state, ability_type)
    ability_name = ABILITIES[ability_type].name
    return ConsumableWasConsumed("New ability: " + ability_name)


def register_summon_scroll():
    consumable_type = ConsumableType.SCROLL_ABILITY_SUMMON
    sprite = Sprite.POTION_SCROLL_ABILITY_SUMMON
    ui_icon_sprite = UiIconSprite.POTION_SCROLL_ABILITY_SUMMON

    register_consumable_effect(consumable_type, _apply)
    image_path = "resources/graphics/icon_scroll_ability_summon.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "It seems to contain powerful knowledge..."
    data = ConsumableData(ui_icon_sprite, sprite, "Dragon's scroll", description, ConsumableCategory.OTHER)
    register_consumable_data(consumable_type, data)
