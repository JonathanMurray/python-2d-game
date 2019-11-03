from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_passive_item


def register_gold_nugget():
    register_passive_item(
        item_type=ItemType.GOLD_NUGGET,
        ui_icon_sprite=UiIconSprite.ITEM_GOLD_NUGGET,
        sprite=Sprite.ITEM_GOLD_NUGGET,
        image_file_path="resources/graphics/item_gold_nugget.png",
        name="Gold nugget",
        description_lines=["It looks expensive..."]
    )
