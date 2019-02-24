from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.BLESSED_SHIELD
HEALTH_REGEN_BOOST = 0.4


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.health_regen += HEALTH_REGEN_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.health_regen -= HEALTH_REGEN_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_blessed_shield_item():
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    register_item_data(
        ITEM_TYPE,
        ItemData(ui_icon_sprite, sprite, "Blessed Shield", "Grants +" + str(HEALTH_REGEN_BOOST) + " health regeneration"))
