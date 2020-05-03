from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ConsumableType, BuffType, Millis, Sprite, PeriodicTimer, SoundId
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite, register_buff_text, ConsumableData, \
    register_consumable_data, ConsumableCategory, register_entity_sprite_initializer, POTION_ENTITY_SIZE
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualRect
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE = BuffType.INVISIBILITY
POTION_TYPE = ConsumableType.INVISIBILITY


def _apply_invis(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INVISIBILITY), Millis(5000))
    return ConsumableWasConsumed()


class Invisibility(AbstractBuffEffect):
    def __init__(self):
        self.timer = PeriodicTimer(Millis(320))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = True

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.game_world.visual_effects.append(
                VisualRect((0, 0, 250), game_state.game_world.player_entity.get_center_position(), 45, 60, Millis(400),
                           1, game_state.game_world.player_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.is_invisible = False

    def get_buff_type(self):
        return BUFF_TYPE


def register_invis_potion():
    ui_icon_sprite = UiIconSprite.POTION_INVISIBILITY
    sprite = Sprite.POTION_INVIS
    register_consumable_effect(POTION_TYPE, _apply_invis)
    register_buff_effect(BUFF_TYPE, Invisibility)
    register_buff_text(BUFF_TYPE, "Invisibility")
    image_path = "resources/graphics/invis_potion.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    data = ConsumableData(ui_icon_sprite, sprite, "Invisibility potion",
                          "Grants temporary invisibility", ConsumableCategory.OTHER, SoundId.CONSUMABLE_BUFF)
    register_consumable_data(POTION_TYPE, data)
