import random

from pythongame.core.buff_effects import get_buff_effect, StatModifyingBuffEffect, register_buff_effect
from pythongame.core.common import ItemType, Sprite, StatModifierInterval, HeroStat, Millis, BuffType
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite, register_buff_text
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_NAME = "Blood amulet"
ITEM_TYPE = ItemType.BLOOD_AMULET
HEALTH_ON_KILL_AMOUNT = 5
PROC_CHANCE = 0.15
BUFF_TYPE = BuffType.ITEM_BLOOD_AMULET
BUFF_LIFE_STEAL_BONUS = 0.2
BUFF_DAMAGE = 0.1
DURATION = Millis(5_000)


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < PROC_CHANCE:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), DURATION)
                player_receive_healing(HEALTH_ON_KILL_AMOUNT, game_state)


class BuffedByBloodAmulet(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.LIFE_STEAL: BUFF_LIFE_STEAL_BONUS,
                                     HeroStat.DAMAGE: BUFF_DAMAGE})


def _register_buff():
    register_buff_text(BUFF_TYPE, ITEM_NAME)
    register_buff_effect(BUFF_TYPE, BuffedByBloodAmulet)


def register_blood_amulet():
    _register_buff()
    item_type = ItemType.BLOOD_AMULET

    register_custom_effect_item(
        item_type=item_type,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_BLOOD_AMULET,
        sprite=Sprite.ITEM_BLOOD_AMULET,
        image_file_path="resources/graphics/item_blood_amulet.png",
        item_equipment_category=ItemEquipmentCategory.NECK,
        name=ITEM_NAME,
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.HEALTH_REGEN, [0.2]),
                                 StatModifierInterval(HeroStat.MAX_MANA, [7]),
                                 StatModifierInterval(HeroStat.MAX_HEALTH, [9])],
        custom_description=[str(int(PROC_CHANCE * 100)) + "% on kill: gain +" + str(
            int(BUFF_LIFE_STEAL_BONUS * 100)) + "% lifesteal and " + str(
            int(BUFF_DAMAGE * 100)) + " attack power for " + "{:.0f}".format(DURATION / 1000) + "s."],
        is_unique=True
    )
