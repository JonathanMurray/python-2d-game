from pythongame.core.common import ItemType
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path
from pythongame.core.game_state import GameState
from pythongame.core.items import register_item_effect, AbstractItemEffect, register_item_ui_icon

SPEED_MULTIPLIER = 0.5


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(SPEED_MULTIPLIER)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-SPEED_MULTIPLIER)

    def get_item_type(self):
        return ItemType.WINGED_BOOTS


def register_winged_boots_item():
    item_type = ItemType.WINGED_BOOTS
    ui_icon_sprite = UiIconSprite.ITEM_WINGED_BOOTS

    register_item_effect(item_type, ItemEffect)
    register_item_ui_icon(item_type, ui_icon_sprite)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_winged_boots.png")
