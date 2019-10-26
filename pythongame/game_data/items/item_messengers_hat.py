from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.MESSENGERS_HAT

SPEED_MULTIPLIER = 0.1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(SPEED_MULTIPLIER)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_entity.add_to_speed_multiplier(-SPEED_MULTIPLIER)

    def get_item_type(self):
        return ITEM_TYPE


def register_messengers_hat_item():
    ui_icon_sprite = UiIconSprite.ITEM_MESSENGERS_HAT
    sprite = Sprite.ITEM_MESSENGERS_HAT
    register_item_effect(ITEM_TYPE, ItemEffect())
    image_file_path = "resources/graphics/item_messengers_hat.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["Increases movement speed by " + str(int(SPEED_MULTIPLIER * 100)) + "%"]
    item_data = ItemData(ui_icon_sprite, sprite, "Messenger's hat", description, ItemEquipmentCategory.HEAD)
    register_item_data(ITEM_TYPE, item_data)
