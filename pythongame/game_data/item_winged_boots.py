from pythongame.core.common import ItemType
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_name
from pythongame.core.game_state import GameState
from pythongame.core.items import register_item_effect, AbstractItemEffect, register_item_ui_icon

ITEM_TYPE = ItemType.WINGED_BOOTS

SPEED_MULTIPLIER = 0.5


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(SPEED_MULTIPLIER)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-SPEED_MULTIPLIER)

    def get_item_type(self):
        return ITEM_TYPE


def register_winged_boots_item():
    ui_icon_sprite = UiIconSprite.ITEM_WINGED_BOOTS

    register_item_effect(ITEM_TYPE, ItemEffect)
    register_item_ui_icon(ITEM_TYPE, ui_icon_sprite)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_winged_boots.png")
    register_item_name(ITEM_TYPE, "Winged Boots")