from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ConsumableType, BuffType, Millis, UiIconSprite, Sprite, PeriodicTimer
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_ui_icon_sprite_path, register_buff_text, \
    register_consumable_data, ConsumableData, ConsumableCategory, register_entity_sprite_initializer, POTION_ENTITY_SIZE
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle

DURATION = Millis(15000)
SPEED_INCREASE = 0.5


def _apply_speed(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INCREASED_MOVE_SPEED), DURATION)
    return ConsumableWasConsumed()


class IncreasedMoveSpeed(AbstractBuffEffect):
    def __init__(self):
        self.timer = PeriodicTimer(Millis(100))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_entity.add_to_speed_multiplier(SPEED_INCREASE)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.player_entity.get_center_position(), 5, 10, Millis(200), 0))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_entity.add_to_speed_multiplier(-SPEED_INCREASE)

    def get_buff_type(self):
        return BuffType.INCREASED_MOVE_SPEED


def register_speed_potion():
    ui_icon_sprite = UiIconSprite.POTION_SPEED
    sprite = Sprite.POTION_SPEED
    register_consumable_effect(ConsumableType.SPEED, _apply_speed)
    register_buff_effect(BuffType.INCREASED_MOVE_SPEED, IncreasedMoveSpeed)
    register_buff_text(BuffType.INCREASED_MOVE_SPEED, "Speed potion")
    image_path = "resources/graphics/white_potion.gif"
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    description = "Gain +" + "{:.0f}".format(SPEED_INCREASE * 100) + "% movement speed for " + \
                  "{:.0f}".format(DURATION / 1000) + "s."
    data = ConsumableData(ui_icon_sprite, sprite, "Speed potion", description, ConsumableCategory.OTHER)
    register_consumable_data(ConsumableType.SPEED, data)
