import random

from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, EnemyDiedEvent, PlayerState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.BLOOD_AMULET
AMOUNT = 1


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, player_state: PlayerState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < 0.5:
                player_state.gain_health(AMOUNT)
                # TODO show healing visually.
                # (This will require passing in game_state which will lead to some more changes)

    def get_item_type(self):
        return ITEM_TYPE


def register_blood_amulet():
    ui_icon_sprite = UiIconSprite.ITEM_BLOOD_AMULET
    sprite = Sprite.ITEM_BLOOD_AMULET
    image_file_path = "resources/graphics/item_blood_amulet.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Blood Amulet"
    description = "Chance to grant +" + str(AMOUNT) + " health on kills"
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, name, description))
