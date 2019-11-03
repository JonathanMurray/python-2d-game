from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_key_item():
    register_passive_item(
        item_type=ItemType.KEY,
        ui_icon_sprite=UiIconSprite.ITEM_KEY,
        sprite=Sprite.ITEM_KEY,
        image_file_path="resources/graphics/item_key.png",
        name="Key",
        description_lines=["It's a small bronze-colored key.", "[Bring it to someone who may know where it leads]"]
    )
