from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_mana
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

MANA_ON_KILL = 3


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            player_receive_mana(MANA_ON_KILL, game_state)


def register_wizards_cowl():
    item_type = ItemType.WIZARDS_COWL
    register_custom_effect_item(
        item_type=item_type,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_WIZARDS_COWL,
        sprite=Sprite.ITEM_WIZARDS_COWL,
        image_file_path="resources/graphics/item_wizards_cowl.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Wizard cowl",
        custom_effect=(ItemEffect()),
        stat_modifier_intervals=[],
        custom_description=["On kill: restore " + str(MANA_ON_KILL) + " mana"]
    )
