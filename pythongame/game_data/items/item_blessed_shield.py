from pythongame.core.common import ItemType, Sprite, UiIconSprite, StatModifierInterval, HeroStat
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_state import GameState, Event, PlayerBlockedEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

HEALING_AMOUNT = 1
ITEM_TYPE = ItemType.BLESSED_SHIELD


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            player_receive_healing(HEALING_AMOUNT, game_state)


def register_blessed_shield_item():
    register_custom_effect_item(
        item_type=ITEM_TYPE,
        item_level=3,
        ui_icon_sprite=UiIconSprite.ITEM_BLESSED_SHIELD,
        sprite=Sprite.ITEM_BLESSED_SHIELD,
        image_file_path="resources/graphics/item_blessed_shield.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Blessed shield",
        custom_description=["On block: gain " + str(HEALING_AMOUNT) + " health"],
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [2]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [5, 6, 7])],
        custom_effect=ItemEffect()
    )
