from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, PlayerState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPES = [ItemType.WIZARDS_COWL]
MANA_AMOUNTS = [5]


class ItemEffect(AbstractItemEffect):

    def __init__(self, amount: int, item_type: ItemType):
        self.amount = amount
        self.item_type = item_type

    def item_handle_event(self, notification: Event, player_state: PlayerState):
        if notification.enemy_died:
            player_state.gain_mana(self.amount)

    def get_item_type(self):
        return self.item_type


def register_wizards_cowl():
    ui_icon_sprite = UiIconSprite.ITEM_WIZARDS_COWL
    sprite = Sprite.ITEM_WIZARDS_COWL
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_wizards_cowl.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_wizards_cowl.png", ITEM_ENTITY_SIZE))
    for i in range(1):
        item_type = ITEM_TYPES[i]
        amount = MANA_AMOUNTS[i]
        register_item_effect(item_type, ItemEffect(amount, item_type))
        name = "Wizard's Cowl"
        description = "Grants +" + str(amount) + " mana on kills"
        register_item_data(item_type, ItemData(ui_icon_sprite, sprite, name, description))
