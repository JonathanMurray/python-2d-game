from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, HeroStat, StatModifierInterval
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerWasAttackedEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

BUFF_TYPE_SLOWED = BuffType.SLOWED_FROM_NOBLE_DEFENDER
SLOW_AMOUNT = 0.3
SLOW_DURATION = Millis(1500)


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerWasAttackedEvent):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_SLOWED), SLOW_DURATION)


class SlowedFromNobleDefender(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE_SLOWED, {HeroStat.MOVEMENT_SPEED: -SLOW_AMOUNT})


def register_noble_defender():
    item_type = ItemType.NOBLE_DEFENDER
    register_custom_effect_item(
        item_type=item_type,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_NOBLE_DEFENDER,
        sprite=Sprite.ITEM_NOBLE_DEFENDER,
        image_file_path="resources/graphics/item_noble_defender.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Noble Defender",
        custom_description=["When you are attacked, your movement speed is slowed by {:.0f}".format(SLOW_AMOUNT * 100) +
                            "% for " + "{:.1f}".format(SLOW_DURATION / 1000) + "s"],
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [4]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [8, 9, 10])],
        custom_effect=ItemEffect()
    )

    register_buff_effect(BUFF_TYPE_SLOWED, SlowedFromNobleDefender)
