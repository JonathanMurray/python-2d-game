from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.WAND
MANA_REGEN_BONUS = 0.3
MAX_MANA_BONUS = 10


class ItemEffect(AbstractItemEffect):

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus += MANA_REGEN_BONUS
        game_state.player_state.mana_resource.increase_max(MAX_MANA_BONUS)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.mana_resource.regen_bonus -= MANA_REGEN_BONUS
        game_state.player_state.mana_resource.decrease_max(MAX_MANA_BONUS)

    def get_item_type(self):
        return ITEM_TYPE


def register_wand_item():
    ui_icon_sprite = UiIconSprite.ITEM_WAND
    sprite = Sprite.ITEM_WAND
    image_file_path = "resources/graphics/item_wand.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(
        sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Wizard's wand"
    description = "Grants " + str(MANA_REGEN_BONUS) + " mana regeneration and +" + str(MAX_MANA_BONUS) + " max mana"
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
