from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.MOLTEN_AXE
DAMAGE_BONUS = 0.15


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus += DAMAGE_BONUS

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus -= DAMAGE_BONUS

    def get_item_type(self):
        return ITEM_TYPE


def register_molten_axe_item():
    ui_icon_sprite = UiIconSprite.ITEM_MOLTEN_AXE
    sprite = Sprite.ITEM_MOLTEN_AXE
    register_item_effect(ITEM_TYPE, ItemEffect())
    image_file_path = "resources/graphics/item_molten_axe.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = ["+" + str(int(round(DAMAGE_BONUS * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, "Molten Axe", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
