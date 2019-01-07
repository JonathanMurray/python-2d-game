from pythongame.core.ability_learning import player_learn_new_ability
from pythongame.core.common import PotionType, Sprite, AbilityType
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, \
    register_ui_icon_sprite_path, UiIconSprite, register_potion_data, PotionData, POTION_ENTITY_SIZE, ABILITIES
from pythongame.core.game_state import GameState
from pythongame.core.potion_effects import PotionWasConsumed, \
    register_potion_effect


def _apply(game_state: GameState):
    ability_type = AbilityType.SUMMON
    player_learn_new_ability(game_state.player_state, ability_type)
    ability_name = ABILITIES[ability_type].name
    return PotionWasConsumed("New ability: " + ability_name)


def register_summon_scroll():
    potion_type = PotionType.SCROLL_ABILITY_SUMMON
    sprite = Sprite.POTION_SCROLL_ABILITY_SUMMON
    ui_icon_sprite = UiIconSprite.POTION_SCROLL_ABILITY_SUMMON

    register_potion_effect(potion_type, _apply)
    image_path = "resources/graphics/icon_scroll_ability_summon.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Learns a new ability"
    register_potion_data(potion_type, PotionData(ui_icon_sprite, sprite, "Scroll", description))
