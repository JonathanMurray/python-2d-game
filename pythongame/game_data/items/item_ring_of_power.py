from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.RING_OF_POWER
MULTIPLIER_BONUS = 0.1


class ItemEffect(AbstractItemEffect):

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus += MULTIPLIER_BONUS

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.damage_modifier_bonus -= MULTIPLIER_BONUS

    def get_item_type(self):
        return ITEM_TYPE


def register_ring_of_power_item():
    ui_icon_sprite = UiIconSprite.ITEM_RING_OF_POWER
    sprite = Sprite.ITEM_RING_OF_POWER
    image_file_path = "resources/graphics/item_ring_of_power.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Ring of Power"
    description = ["+" + str(int(round(MULTIPLIER_BONUS * 100))) + "% damage"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.RING)
    register_item_data(ITEM_TYPE, item_data)
