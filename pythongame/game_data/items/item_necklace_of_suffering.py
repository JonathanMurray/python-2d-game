from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, StatModifyingBuffEffect
from pythongame.core.common import ItemType, UiIconSprite, Sprite, HeroStat, Event, BuffType, Millis, \
    StatModifierInterval
from pythongame.core.game_state import GameState, PlayerLostHealthEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

BUFF_TYPE = BuffType.INCREASED_DAMAGE_FROM_NECKLACE_OF_SUFFERING
BUFF_DURATION = Millis(3000)
BUFF_DAMAGE = 0.2
ITEM_TYPE = ItemType.NECKLACE_OF_SUFFERING


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerLostHealthEvent):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)


class BuffEffect(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.DAMAGE: BUFF_DAMAGE})


def register_necklace_of_suffering_item():
    register_custom_effect_item(
        item_type=ITEM_TYPE,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_NECKLACE_OF_SUFFERING,
        sprite=Sprite.ITEM_NECKLACE_OF_SUFFERING,
        image_file_path="resources/graphics/item_necklace_of_suffering.png",
        item_equipment_category=ItemEquipmentCategory.NECK,
        name="Necklace of Domination",
        custom_description=["Any time you lose health, gain +" + str(int(BUFF_DAMAGE * 100)) +
                            " attack power for " + "{:.0f}".format(BUFF_DURATION / 1000) + "s"],
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.DAMAGE, [0.1])],
        is_unique=True
    )
    register_buff_effect(BUFF_TYPE, BuffEffect)
