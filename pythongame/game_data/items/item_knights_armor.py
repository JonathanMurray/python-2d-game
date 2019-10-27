from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.KNIGHTS_ARMOR
ARMOR_BOOST = 2
SPEED_DECREASE = 0.05


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus += ARMOR_BOOST
        game_state.player_entity.add_to_speed_multiplier(-SPEED_DECREASE)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus -= ARMOR_BOOST
        game_state.player_entity.add_to_speed_multiplier(SPEED_DECREASE)

    def get_item_type(self):
        return ITEM_TYPE


def register_knights_armor():
    ui_icon_sprite = UiIconSprite.ITEM_KNIGHTS_ARMOR
    sprite = Sprite.ITEM_KNIGHTS_ARMOR
    image_file_path = "resources/graphics/item_knights_armor.png"
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = [str(ARMOR_BOOST) + " armor",
                   "Reduces movement speed by {:.0f}".format(SPEED_DECREASE * 100) + "%"]
    item_data = ItemData(ui_icon_sprite, sprite, "Knight's Armor", description, ItemEquipmentCategory.CHEST)
    register_item_data(ITEM_TYPE, item_data)
