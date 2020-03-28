from pythongame.core.common import HeroStat, StatModifierInterval
from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerLostHealthEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerLostHealthEvent):
            absorb_amount = event.amount * 0.25
            if absorb_amount <= game_state.player_state.mana_resource.value:
                game_state.player_state.mana_resource.lose(absorb_amount)
                player_receive_healing(absorb_amount, game_state)


def register_lich_armor_item():
    register_custom_effect_item(
        item_type=ItemType.LICH_ARMOR,
        item_level=7,
        ui_icon_sprite=UiIconSprite.ITEM_LICH_ARMOR,
        sprite=Sprite.ITEM_LICH_ARMOR,
        image_file_path="resources/graphics/item_lich_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name="Lich armor",
        custom_description=["25% of damage taken is instead drained from your mana"],
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MAX_MANA, [30]),
                                 StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, [0.05])],
        is_unique=True
    )
