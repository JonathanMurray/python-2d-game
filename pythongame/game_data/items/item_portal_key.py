from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_quest_item


def register_portal_key_item():
    register_quest_item(
        item_type=ItemType.PORTAL_KEY,
        ui_icon_sprite=UiIconSprite.ITEM_PORTAL_KEY,
        sprite=Sprite.ITEM_PORTAL_KEY,
        image_file_path="resources/graphics/item_portal_key.png",
        name="Portal key",
        description_lines=["Use this to pass through portals!"]
    )
