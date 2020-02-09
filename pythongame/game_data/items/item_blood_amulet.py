import random

from pythongame.core.common import ItemType, Sprite, ItemId, plain_item_id
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE, register_item_level
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.BLOOD_AMULET
HEALTH_ON_KILL_AMOUNT = 5
PROC_CHANCE = 0.3


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_id: ItemId):
        super().__init__(item_id)

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < PROC_CHANCE:
                player_receive_healing(HEALTH_ON_KILL_AMOUNT, game_state)


def register_blood_amulet():
    item_id = plain_item_id(ITEM_TYPE)
    register_item_level(ITEM_TYPE, 4)
    ui_icon_sprite = UiIconSprite.ITEM_BLOOD_AMULET
    sprite = Sprite.ITEM_BLOOD_AMULET
    image_file_path = "resources/graphics/item_blood_amulet.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(item_id, ItemEffect(item_id))
    name = "Blood Amulet"
    description = [str(int(PROC_CHANCE * 100)) + "% on kill: gain " + str(HEALTH_ON_KILL_AMOUNT) + " health"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.NECK)
    register_item_data(item_id, item_data)
