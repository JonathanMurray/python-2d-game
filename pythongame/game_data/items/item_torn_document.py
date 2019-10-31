from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.TORN_DOCUMENT


class ItemEffect(AbstractItemEffect):
    def get_item_type(self):
        return ITEM_TYPE


def register_torn_document_item():
    ui_icon_sprite = UiIconSprite.ITEM_TORN_DOCUMENT
    sprite = Sprite.ITEM_TORN_DOCUMENT
    image_file_path = "resources/graphics/item_torn_document.png"
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["This piece of paper is torn and crumpled, and its text seems to be written in an arcane language.",
                   "[Bring it to someone who can make sense of it]"]
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, "Torn document", description))
