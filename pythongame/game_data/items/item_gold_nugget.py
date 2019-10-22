from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.GOLD_NUGGET


class ItemEffect(AbstractItemEffect):
    def get_item_type(self):
        return ITEM_TYPE


def register_gold_nugget():
    ui_icon_sprite = UiIconSprite.ITEM_GOLD_NUGGET
    sprite = Sprite.ITEM_GOLD_NUGGET
    image_file_path = "resources/graphics/item_gold_nugget.png"
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["It looks expensive..."]
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, "Gold nugget", description))
