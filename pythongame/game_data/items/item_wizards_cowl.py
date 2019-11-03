from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_mana
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        super().__init__(item_type)
        self.mana_on_kill = 5

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            player_receive_mana(self.mana_on_kill, game_state)

    def get_description(self):
        return ["On kill: restore " + str(self.mana_on_kill) + " mana"]


def register_wizards_cowl():
    item_type = ItemType.WIZARDS_COWL
    effect = ItemEffect(item_type)
    register_custom_effect_item(
        item_type=item_type,
        ui_icon_sprite=UiIconSprite.ITEM_WIZARDS_COWL,
        sprite=Sprite.ITEM_WIZARDS_COWL,
        image_file_path="resources/graphics/item_wizards_cowl.png",
        item_equipment_category=ItemEquipmentCategory.HEAD,
        name="Wizard's Cowl",
        item_effect=effect
    )
