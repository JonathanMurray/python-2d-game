from pythongame.core.common import ItemType
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_name
from pythongame.core.game_state import GameState
from pythongame.core.items import register_item_effect, AbstractItemEffect, register_item_ui_icon

ITEM_TYPE = ItemType.AMULET_OF_MANA

MANA_REGEN_BOOST = 0.002


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.mana_regen += MANA_REGEN_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.mana_regen -= MANA_REGEN_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_amulet_of_mana_item():
    ui_icon_sprite = UiIconSprite.ITEM_AMULET_OF_MANA

    register_item_effect(ITEM_TYPE, ItemEffect)
    register_item_ui_icon(ITEM_TYPE, ui_icon_sprite)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_amulet.png")
    register_item_name(ITEM_TYPE, "Amulet of Mana")