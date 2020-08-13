from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import AbilityResult, AbilityWasUsedSuccessfully, register_ability_effect, \
    AbilityFailedToExecute
from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, StatModifyingBuffEffect
from pythongame.core.common import HeroStat, BuffType, StatModifierInterval
from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, AbilityType
from pythongame.core.game_data import register_buff_text
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_NAME = "Taskmaster's whip"
ABILITY_TYPE = AbilityType.ITEM_WHIP
BUFF_TYPE = BuffType.ITEM_WHIP
ABILITY_HEALTH_LOSS = 10
BUFF_DAMAGE = 0.15
DURATION = Millis(8_000)
ABILITY_DESCRIPTION = "Pay " + str(ABILITY_HEALTH_LOSS) + " health and gain + " + str(
    int(BUFF_DAMAGE * 100)) + " attack power for " + \
                      "{:.0f}".format(DURATION / 1000) + "s."


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_state = game_state.player_state
    if player_state.health_resource.value <= ABILITY_HEALTH_LOSS:
        return AbilityFailedToExecute("Using this would kill you!")
    player_state.health_resource.lose(ABILITY_HEALTH_LOSS)
    player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)
    return AbilityWasUsedSuccessfully()


def _register_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    # TODO sound effect
    ability_data = AbilityData(ITEM_NAME, UiIconSprite.ITEM_WHIP, 0, Millis(8_000), ABILITY_DESCRIPTION,
                               sound_id=None, is_item_ability=True)
    register_ability_data(ABILITY_TYPE, ability_data)


class BuffedByWhip(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.DAMAGE: BUFF_DAMAGE})


def _register_buff():
    register_buff_text(BUFF_TYPE, ITEM_NAME)
    register_buff_effect(BUFF_TYPE, BuffedByWhip)


def register_whip_item():
    _register_buff()
    _register_ability()

    register_custom_effect_item(
        item_type=ItemType.WHIP,
        ui_icon_sprite=UiIconSprite.ITEM_WHIP,
        sprite=Sprite.ITEM_WHIP,
        image_file_path="resources/graphics/item_whip.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name=ITEM_NAME,
        stat_modifier_intervals=[StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, [0.18]),
                                 StatModifierInterval(HeroStat.LIFE_STEAL, [0.07]),
                                 StatModifierInterval(HeroStat.LIFE_ON_KILL, [1])],
        custom_effect=AbstractItemEffect(),
        custom_description=["Active: " + ABILITY_DESCRIPTION],
        item_level=5,
        is_unique=True,
        active_ability_type=ABILITY_TYPE
    )
