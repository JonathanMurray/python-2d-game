import random

from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.BLOOD_AMULET
AMOUNT = 1


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < 0.5:
                player_receive_healing(AMOUNT, game_state)

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
    description = "Gives a chance to restore " + str(AMOUNT) + " health on kills"
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, name, description))