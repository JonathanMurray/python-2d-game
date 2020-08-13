from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import AbilityResult, AbilityWasUsedSuccessfully, register_ability_effect
from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, StatModifyingBuffEffect
from pythongame.core.common import HeroStat, BuffType, StatModifierInterval
from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, AbilityType
from pythongame.core.game_data import register_buff_text
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_NAME = "Eternal Light"
ABILITY_TYPE = AbilityType.ITEM_CANDLE
BUFF_TYPE = BuffType.ITEM_CANDLE
HEALTH_REGEN_INCREASE = 1
DURATION = Millis(10_000)
ABILITY_DESCRIPTION = "Gain +" + str(HEALTH_REGEN_INCREASE) + " health regen for " + \
                      "{:.0f}".format(DURATION / 1000) + "s."


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)
    return AbilityWasUsedSuccessfully()


def _register_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    ability_data = AbilityData(ITEM_NAME, UiIconSprite.ITEM_CANDLE, 7, Millis(16_000), ABILITY_DESCRIPTION,
                               sound_id=None, is_item_ability=True)
    register_ability_data(ABILITY_TYPE, ability_data)


class BuffedByCandle(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.HEALTH_REGEN: HEALTH_REGEN_INCREASE})


def _register_buff():
    register_buff_text(BUFF_TYPE, ITEM_NAME)
    register_buff_effect(BUFF_TYPE, BuffedByCandle)


def register_candle_item():
    _register_buff()
    _register_ability()

    register_custom_effect_item(
        item_type=ItemType.CANDLE,
        ui_icon_sprite=UiIconSprite.ITEM_CANDLE,
        sprite=Sprite.ITEM_CANDLE,
        image_file_path="resources/graphics/item_candle.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name=ITEM_NAME,
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, [0.12]),
                                 StatModifierInterval(HeroStat.MAX_MANA, [10]),
                                 StatModifierInterval(HeroStat.MANA_REGEN, [0.1])],
        custom_effect=AbstractItemEffect(),
        custom_description=["Active: " + ABILITY_DESCRIPTION],
        item_level=3,
        is_unique=True,
        active_ability_type=ABILITY_TYPE
    )
