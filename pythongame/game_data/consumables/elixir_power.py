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
from pythongame.core.visual_effects import VisualRect
from pythongame.core.world_entity import WorldEntity

DURATION = Millis(30_000)
DAMAGE_MODIFIER_INCREASE = 0.3
BUFF_TYPE = BuffType.ELIXIR_OF_POWER


def _apply(game_state: GameState):
    create_potion_visual_effect_at_player(game_state)
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)
    return ConsumableWasConsumed()


class BuffedFromElixirOfPower(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.DAMAGE: DAMAGE_MODIFIER_INCREASE})
        self.timer = PeriodicTimer(Millis(300))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.game_world.visual_effects.append(
                VisualRect((0, 0, 0), game_state.game_world.player_entity.get_center_position(), 6, 18, Millis(200), 3))


def register_elixir_of_power():
    ui_icon_sprite = UiIconSprite.ELIXIR_POWER
    sprite = Sprite.ELIXIR_POWER
    consumable_type = ConsumableType.POWER
    register_consumable_level(consumable_type, 6)
    register_consumable_effect(consumable_type, _apply)
    register_buff_effect(BUFF_TYPE, BuffedFromElixirOfPower)
    name = "Elixir of Power"
    register_buff_text(BUFF_TYPE, name)
    image_path = "resources/graphics/item_elixir_of_power.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_path, POTION_ENTITY_SIZE))
    description = "Gain +" + "{:.0f}".format(DAMAGE_MODIFIER_INCREASE * 100) + " attack power for " + \
                  "{:.0f}".format(DURATION / 1000) + "s."
    data = ConsumableData(ui_icon_sprite, sprite, name, description, ConsumableCategory.OTHER, SoundId.CONSUMABLE_BUFF)
    register_consumable_data(consumable_type, data)
