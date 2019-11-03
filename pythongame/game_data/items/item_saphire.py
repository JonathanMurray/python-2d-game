from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_saphire():
    register_passive_item(
        item_type=ItemType.SAPHIRE,
        ui_icon_sprite=UiIconSprite.ITEM_SAPHIRE,
        sprite=Sprite.ITEM_SAPHIRE,
        image_file_path="resources/graphics/item_saphire.png",
        name="Saphire",
        description_lines=["It looks expensive..."]
    )
