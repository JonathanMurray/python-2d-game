from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_sapphire():
    register_passive_item(
        item_type=ItemType.SAPPHIRE,
        ui_icon_sprite=UiIconSprite.ITEM_SAPPHIRE,
        sprite=Sprite.ITEM_SAPPHIRE,
        image_file_path="resources/graphics/item_sapphire.png",
        name="Sapphire",
        description_lines=["It looks expensive..."]
    )
