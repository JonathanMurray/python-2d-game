from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_torn_document_item():
    register_passive_item(
        item_type=ItemType.TORN_DOCUMENT,
        ui_icon_sprite=UiIconSprite.ITEM_TORN_DOCUMENT,
        sprite=Sprite.ITEM_TORN_DOCUMENT,
        image_file_path="resources/graphics/item_torn_document.png",
        name="Torn document",
        description_lines=[
            "This piece of paper is torn and crumpled, and its text seems to be written in an arcane language.",
            "[Bring it to someone who can make sense of it]"]
    )
