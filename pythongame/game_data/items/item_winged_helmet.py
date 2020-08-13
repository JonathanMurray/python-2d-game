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

ITEM_NAME = "Apollo's crown"
ABILITY_TYPE = AbilityType.ITEM_WINGED_HELMET
BUFF_TYPE = BuffType.ITEM_WINGED_HELMET
DODGE_MODIFIER_INCREASE = 0.25
DURATION = Millis(5_000)
ABILITY_DESCRIPTION = "Gain +" + "{:.0f}".format(DODGE_MODIFIER_INCREASE * 100) + "% dodge chance for " + \
                      "{:.0f}".format(DURATION / 1000) + "s."


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)
    return AbilityWasUsedSuccessfully()


def _register_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    ability_data = AbilityData(ITEM_NAME, UiIconSprite.ITEM_WINGED_HELMET, 5, Millis(30_000), ABILITY_DESCRIPTION,
                               sound_id=None, is_item_ability=True)
    register_ability_data(ABILITY_TYPE, ability_data)


class BuffedByWingedHelmet(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.DODGE_CHANCE: DODGE_MODIFIER_INCREASE})


def _register_buff():
    register_buff_text(BUFF_TYPE, ITEM_NAME)
    register_buff_effect(BUFF_TYPE, BuffedByWingedHelmet)


def register_winged_helmet_item():
    _register_buff()
    _register_ability()

    register_custom_effect_item(
        item_type=ItemType.WINGED_HELMET,
        ui_icon_sprite=UiIconSprite.ITEM_WINGED_HELMET,
        sprite=Sprite.ITEM_WINGED_HELMET,
        image_file_path="resources/graphics/item_winged_helmet.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name=ITEM_NAME,
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [3]),
                                 StatModifierInterval(HeroStat.MOVEMENT_SPEED, [0.18])],
        custom_effect=AbstractItemEffect(),
        custom_description=["Active: " + ABILITY_DESCRIPTION],
        item_level=6,
        is_unique=True,
        active_ability_type=ABILITY_TYPE
    )
