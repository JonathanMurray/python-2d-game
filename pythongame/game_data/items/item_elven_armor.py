from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.ELVEN_ARMOR
MANA_REGEN_BOOST = 0.5
MANA_BOOST = 15


class ItemEffect(AbstractItemEffect):

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.mana_regen_bonus += MANA_REGEN_BOOST
        game_state.player_state.max_mana += MANA_BOOST
        game_state.player_state.gain_max_mana(MANA_BOOST)

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.mana_regen_bonus -= MANA_REGEN_BOOST
        game_state.player_state.lose_max_mana(MANA_BOOST)

    def get_item_type(self):
        return ITEM_TYPE


def register_elven_armor():
    ui_icon_sprite = UiIconSprite.ITEM_ELVEN_ARMOR
    sprite = Sprite.ITEM_ELVEN_ARMOR
    image_file_path = "resources/graphics/item_elven_armor.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Elven Armor"
    description = "Grants +" + str(MANA_REGEN_BOOST) + " mana regeneration and +" + str(MANA_BOOST) + " max mana."
    register_item_data(ITEM_TYPE, ItemData(ui_icon_sprite, sprite, name, description))
