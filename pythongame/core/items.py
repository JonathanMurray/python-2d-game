from typing import Dict, Type

from pythongame.core.common import *
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import GameState


class AbstractItemEffect:
    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass

    def get_item_type(self):
        pass


_item_effects: Dict[ItemType, Type[AbstractItemEffect]] = {}

_item_ui_icon_sprites: Dict[ItemType, UiIconSprite] = {}


def register_item_effect(item_type: ItemType, effect: Type[AbstractItemEffect]):
    _item_effects[item_type] = effect


def register_item_ui_icon(item_type: ItemType, ui_icon_sprite: UiIconSprite):
    _item_ui_icon_sprites[item_type] = ui_icon_sprite


def get_item_effect(item_type: ItemType) -> AbstractItemEffect:
    return _item_effects[item_type]()


def get_item_ui_icon_sprite(item_type: ItemType) -> UiIconSprite:
    return _item_ui_icon_sprites[item_type]
