from typing import List

from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerBlockedEvent
from pythongame.core.item_effects import StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, item_type: ItemType):
        super().__init__(item_type, {HeroStat.ARMOR: 2, HeroStat.BLOCK_AMOUNT: 7})
        self.damage_amount = 5

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            deal_player_damage_to_enemy(game_state, event.npc_attacker, self.damage_amount, DamageType.MAGIC)

    def get_description(self) -> List[str]:
        return super().get_description() + ["On block: deal " + str(self.damage_amount) + " magic damage to attacker"]


def register_skull_shield_item():
    item_type = ItemType.SKULL_SHIELD
    effect = ItemEffect(item_type)
    register_custom_effect_item(
        item_type=item_type,
        ui_icon_sprite=UiIconSprite.ITEM_SKULL_SHIELD,
        sprite=Sprite.ITEM_SKULL_SHIELD,
        image_file_path="resources/graphics/item_skull_shield.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Skull shield",
        item_effect=effect
    )
