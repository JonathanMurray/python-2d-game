from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.game_data.items.register_items_util import register_quest_item


def register_corrupted_orb_item():
    register_quest_item(
        item_type=ItemType.QUEST_CORRUPTED_ORB,
        ui_icon_sprite=UiIconSprite.ITEM_CORRUPTED_ORB,
        sprite=Sprite.ITEM_CORRUPTED_ORB,
        image_file_path="resources/graphics/item_corrupted_orb.png",
        name="Corrupted Orb",
        description_lines=["It emanates dark energies"]
    )
