from pythongame.core.common import ItemType
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path
from pythongame.core.game_state import GameState
from pythongame.core.items import register_item_effect, AbstractItemEffect, register_item_ui_icon

ITEM_TYPE = ItemType.SWORD_OF_LEECHING
LIFE_STEAL_BOOST = 0.1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.life_steal_ratio += LIFE_STEAL_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.life_steal_ratio -= LIFE_STEAL_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_sword_of_leeching_item():
    ui_icon_sprite = UiIconSprite.ITEM_SWORD_OF_LEECHING

    register_item_effect(ITEM_TYPE, ItemEffect)
    register_item_ui_icon(ITEM_TYPE, ui_icon_sprite)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_sword_of_leeching.png")