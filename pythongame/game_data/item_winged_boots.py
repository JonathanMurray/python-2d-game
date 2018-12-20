from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.WINGED_BOOTS

SPEED_MULTIPLIER = 0.3


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(SPEED_MULTIPLIER)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-SPEED_MULTIPLIER)

    def get_item_type(self):
        return ITEM_TYPE


def register_winged_boots_item():
    ui_icon_sprite = UiIconSprite.ITEM_WINGED_BOOTS
    sprite = Sprite.ITEM_WINGED_BOOTS
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_winged_boots.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_winged_boots.png", ITEM_ENTITY_SIZE))
    register_item_data(
        ITEM_TYPE,
        ItemData(ui_icon_sprite, sprite, "Winged Boots", "Grants increased movement speed"))
