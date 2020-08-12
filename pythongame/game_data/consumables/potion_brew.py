from typing import Optional

from pythongame.core.buff_effects import AbstractBuffEffect, get_buff_effect, register_buff_effect
from pythongame.core.common import ConsumableType, Sprite, UiIconSprite, Millis, BuffType, PeriodicTimer, SoundId
from pythongame.core.consumable_effects import ConsumableWasConsumed, \
    register_consumable_effect, ConsumableFailedToBeConsumed
from pythongame.core.damage_interactions import player_receive_healing, player_receive_mana
from pythongame.core.game_data import register_entity_sprite_initializer, register_ui_icon_sprite_path, \
    register_consumable_data, ConsumableData, POTION_ENTITY_SIZE, ConsumableCategory, \
    register_buff_text, register_consumable_level
from pythongame.core.game_state import GameState, NonPlayerCharacter, Event, PlayerLostHealthEvent, \
    BuffEventOutcome
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.world_entity import WorldEntity

BUFF_DURATION = Millis(10000)
BUFF_TYPE = BuffType.RESTORING_HEALTH_FROM_BREW


def _apply(game_state: GameState):
    player_state = game_state.player_state
    if not (player_state.health_resource.is_at_max() and player_state.mana_resource.is_at_max()):
        player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)
        return ConsumableWasConsumed()
    else:
        return ConsumableFailedToBeConsumed("Already at full health and mana!")


class RestoringHealthFromBrew(AbstractBuffEffect):
    def __init__(self):
        self.timer = PeriodicTimer(Millis(600))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            player_receive_healing(3, game_state)
            player_receive_mana(3, game_state)

    def get_buff_type(self):
        return BUFF_TYPE

    def buff_handle_event(self, event: Event) -> Optional[BuffEventOutcome]:
        if isinstance(event, PlayerLostHealthEvent):
            return BuffEventOutcome.cancel_effect()


def register_brew_potion():
    consumable_type = ConsumableType.BREW
    sprite = Sprite.POTION_BREW
    ui_icon_sprite = UiIconSprite.POTION_BREW
    register_consumable_level(consumable_type, 2)
    register_consumable_effect(consumable_type, _apply)
    image_path = "resources/graphics/icon_potion_brew.png"
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    description = "Slowly restores health and mana over " + "{:.0f}".format(BUFF_DURATION / 1000) + \
                  "s. Only works outside of combat."
    data = ConsumableData(ui_icon_sprite, sprite, "Brew", description, ConsumableCategory.HEALTH,
                          SoundId.CONSUMABLE_POTION)
    register_consumable_data(consumable_type, data)

    register_buff_effect(BUFF_TYPE, RestoringHealthFromBrew)
    register_buff_text(BUFF_TYPE, "Recovering")
