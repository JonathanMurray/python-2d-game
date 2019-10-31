from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

ITEM_TYPE = ItemType.HATCHET
DAMAGE_BONUS = 0.1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus += DAMAGE_BONUS

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BONUS

    def get_item_type(self):
        return ITEM_TYPE


def register_hatchet_item():
    ui_icon_sprite = UiIconSprite.ITEM_HATCHET
    sprite = Sprite.ITEM_HATCHET
    register_item_effect(ITEM_TYPE, ItemEffect())
    image_file_path = "resources/graphics/item_hatchet.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["+" + str(int(round(DAMAGE_BONUS * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, "Hatchet", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
