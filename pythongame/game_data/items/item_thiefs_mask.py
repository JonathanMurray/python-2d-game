from pythongame.core.common import HeroStat, StatModifierInterval
from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_mana
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerDodgedEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

MANA_ON_DODGE_AMOUNT = 5


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDodgedEvent):
            player_receive_mana(MANA_ON_DODGE_AMOUNT, game_state)


def register_thiefs_mask_item():
    register_custom_effect_item(
        item_type=ItemType.THIEFS_MASK,
        ui_icon_sprite=UiIconSprite.ITEM_THIEFS_MASK,
        sprite=Sprite.ITEM_THIEFS_MASK,
        image_file_path="resources/graphics/item_thiefs_mask.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Mask of Thieves",
        custom_description=["On dodge: gain " + str(MANA_ON_DODGE_AMOUNT) + " mana"],
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.DODGE_CHANCE, [0.09]),
                                 StatModifierInterval(HeroStat.DAMAGE, [0.12]),
                                 StatModifierInterval(HeroStat.MANA_REGEN, [0.05])],
        is_unique=True
    )
