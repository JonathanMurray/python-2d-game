from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, StatModifyingBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, HeroStat
from pythongame.core.game_data import UiIconSprite, register_buff_text
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

BUFF_TYPE = BuffType.BUFFED_BY_HEALING_WAND
HEALTH_REGEN_BONUS = 1
BUFF_DURATION = Millis(5000)


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)


class BuffedByHealingWand(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.HEALTH_REGEN: HEALTH_REGEN_BONUS})


def register_healing_wand_item():
    item_type = ItemType.HEALING_WAND
    register_custom_effect_item(
        item_type=item_type,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_HEALING_WAND,
        sprite=Sprite.ITEM_HEALING_WAND,
        image_file_path="resources/graphics/item_healing_wand.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Healing wand",
        custom_description=["When you damage an enemy, gain +" + str(HEALTH_REGEN_BONUS) + " health regen for " +
                            "{:.0f}".format(BUFF_DURATION / 1000) + "s"],
        stat_modifier_intervals=[],
        custom_effect=ItemEffect()
    )

    register_buff_effect(BUFF_TYPE, BuffedByHealingWand)
    register_buff_text(BUFF_TYPE, "Healing wand")
