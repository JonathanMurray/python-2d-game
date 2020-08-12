import random

from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, BuffType, Millis, PeriodicTimer, \
    StatModifierInterval
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_state import Event, GameState, PlayerDamagedEnemy, NonPlayerCharacter
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_TYPE = ItemType.CLEAVER
PROC_CHANCE = 0.2
BUFF_TYPE = BuffType.BLEEDING_FROM_CLEAVER_WEAPON
BUFF_DURATION = Millis(10_000)
DAMAGE_INTERVAL = Millis(750)
DAMAGE = 1
TOTAL_DAMAGE = int(float(BUFF_DURATION / DAMAGE_INTERVAL))
DAMAGE_SOURCE = "cleaver_bleed"


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            if event.damage_source != DAMAGE_SOURCE:  # the bleed shouldn't trigger new bleeds
                if random.random() < PROC_CHANCE:
                    event.enemy_npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)


class BuffEffect(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(DAMAGE_INTERVAL)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            deal_player_damage_to_enemy(game_state, buffed_npc, DAMAGE, DamageType.PHYSICAL,
                                        damage_source=DAMAGE_SOURCE)

    def get_buff_type(self):
        return BUFF_TYPE


def register_cleaver_item():
    register_custom_effect_item(
        item_type=ITEM_TYPE,
        item_level=7,
        ui_icon_sprite=UiIconSprite.ITEM_CLEAVER,
        sprite=Sprite.ITEM_CLEAVER,
        image_file_path="resources/graphics/item_cleaver.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="The Cleaver",
        custom_effect=ItemEffect(),
        custom_description=[str(
            int(PROC_CHANCE * 100)) + "% on hit: cause enemy to bleed, taking " + str(TOTAL_DAMAGE) + \
                            " physical damage over " + "{:.0f}".format(BUFF_DURATION / 1000) + "s"],
        stat_modifier_intervals=[StatModifierInterval(HeroStat.PHYSICAL_DAMAGE, [0.41])],
        is_unique=True
    )
    register_buff_effect(BUFF_TYPE, BuffEffect)
