from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_mana
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.WIZARDS_COWL
MANA_AMOUNT_ON_KILL = 5


class ItemEffect(AbstractItemEffect):

    def __init__(self, amount: int, item_type: ItemType):
        self.amount = amount
        self.item_type = item_type

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            player_receive_mana(self.amount, game_state)

    def get_item_type(self):
        return self.item_type


def register_wizards_cowl():
    ui_icon_sprite = UiIconSprite.ITEM_WIZARDS_COWL
    sprite = Sprite.ITEM_WIZARDS_COWL
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_wizards_cowl.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_wizards_cowl.png", ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect(MANA_AMOUNT_ON_KILL, ITEM_TYPE))
    name = "Wizard's Cowl"
    description = ["On kill: restore " + str(MANA_AMOUNT_ON_KILL) + " mana"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.HEAD)
    register_item_data(ITEM_TYPE, item_data)
