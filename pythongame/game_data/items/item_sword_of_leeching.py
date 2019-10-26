from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.SWORD_OF_LEECHING
LIFE_STEAL_BOOST = 0.1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.life_steal_ratio += LIFE_STEAL_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.life_steal_ratio -= LIFE_STEAL_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_sword_of_leeching_item():
    ui_icon_sprite = UiIconSprite.ITEM_SWORD_OF_LEECHING
    sprite = Sprite.ITEM_SWORD_OF_LEECHING
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_sword_of_leeching.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_sword_of_leeching.png", ITEM_ENTITY_SIZE))
    description = ["+" + str(int(LIFE_STEAL_BOOST * 100)) + "% life steal"]
    item_data = ItemData(ui_icon_sprite, sprite, "Sword of Leeching", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
