from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.WOODEN_SHIELD
ARMOR_BOOST = 1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus -= ARMOR_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_wooden_shield():
    ui_icon_sprite = UiIconSprite.ITEM_WOODEN_SHIELD
    sprite = Sprite.ITEM_WOODEN_SHIELD
    image_file_path = "resources/graphics/item_wooden_shield.png"
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = "Gives +" + str(ARMOR_BOOST) + " armor"
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, "Wooden Shield", description))
