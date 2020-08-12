from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_quest_item


def register_quest_key_item():
    register_quest_item(
        item_type=ItemType.QUEST_KEY,
        ui_icon_sprite=UiIconSprite.ITEM_KEY,
        sprite=Sprite.ITEM_KEY,
        image_file_path="resources/graphics/item_key.png",
        name="Rusty key",
        description_lines=["Bring it to someone who may know where it leads"]
    )
