from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import ConsumableType, BuffType, Millis, UiIconSprite, Sprite, PeriodicTimer, SoundId, \
    HeroStat
from pythongame.core.consumable_effects import create_potion_visual_effect_at_player, ConsumableWasConsumed, \
    register_consumable_effect
from pythongame.core.game_data import register_ui_icon_sprite_path, register_buff_text, \
    register_consumable_data, ConsumableData, ConsumableCategory, register_entity_sprite_initializer, \
    POTION_ENTITY_SIZE, register_consumable_level
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE = BuffType.INCREASED_MOVE_SPEED

DURATION = Millis(15000)
SPEED_INCREASE = 0.4


def _apply_speed(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.INCREASED_MOVE_SPEED), DURATION)
    return ConsumableWasConsumed()


class IncreasedMoveSpeed(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.MOVEMENT_SPEED: SPEED_INCREASE})
        self.timer = PeriodicTimer(Millis(100))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.game_world.visual_effects.append(
                VisualCircle((150, 200, 250), game_state.game_world.player_entity.get_center_position(), 5, 10,
                             Millis(200), 0))

    def get_buff_type(self):
        return BUFF_TYPE


def register_speed_potion():
    ui_icon_sprite = UiIconSprite.POTION_SPEED
    sprite = Sprite.POTION_SPEED
    consumable_type = ConsumableType.SPEED
    register_consumable_effect(consumable_type, _apply_speed)
    register_consumable_level(consumable_type, 5)
    register_buff_effect(BUFF_TYPE, IncreasedMoveSpeed)
    register_buff_text(BUFF_TYPE, "Speed potion")
    image_path = "resources/graphics/item_speed_potion.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    description = "Gain +" + "{:.0f}".format(SPEED_INCREASE * 100) + "% movement speed for " + \
                  "{:.0f}".format(DURATION / 1000) + "s."
    data = ConsumableData(ui_icon_sprite, sprite, "Speed potion", description, ConsumableCategory.OTHER,
                          SoundId.CONSUMABLE_BUFF)
    register_consumable_data(consumable_type, data)
