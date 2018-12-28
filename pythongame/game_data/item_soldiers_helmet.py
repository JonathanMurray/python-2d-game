from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.SOLDIERS_HELMET
HEALTH_AMOUNT = 25


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.gain_max_health(HEALTH_AMOUNT)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.lose_max_health(HEALTH_AMOUNT)

    def get_item_type(self):
        return ITEM_TYPE


def register_soldiers_helmet_item():
    ui_icon_sprite = UiIconSprite.ITEM_SOLDIERS_HELMET
    sprite = Sprite.ITEM_SOLDIERS_HELMET
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_soldiers_helmet.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_soldiers_helmet.png", ITEM_ENTITY_SIZE))
    register_item_data(
        ITEM_TYPE,
        ItemData(ui_icon_sprite, sprite, "Soldier's Helmet", "Grants +" + str(HEALTH_AMOUNT) + " max health"))
