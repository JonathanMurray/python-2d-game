from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_frog_item():
    register_passive_item(
        item_type=ItemType.FROG,
        ui_icon_sprite=UiIconSprite.ITEM_FROG,
        sprite=Sprite.ITEM_FROG,
        image_file_path="resources/graphics/item_frog.png",
        name="Frog",
        description_lines=["Who could this belong to?"]
    )
