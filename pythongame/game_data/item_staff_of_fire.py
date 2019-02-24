from pythongame.core.common import ItemType, Sprite
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect

ITEM_TYPE = ItemType.STAFF_OF_FIRE
FIREBALL_DAMAGE_BOOST = 1


class ItemEffect(AbstractItemEffect):
    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.fireball_dmg_boost += FIREBALL_DAMAGE_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.fireball_dmg_boost -= FIREBALL_DAMAGE_BOOST

    def get_item_type(self):
        return ITEM_TYPE


def register_staff_of_fire_item():
    ui_icon_sprite = UiIconSprite.ITEM_STAFF_OF_FIRE
    sprite = Sprite.ITEM_STAFF_OF_FIRE
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_staff_of_fire.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_staff_of_fire.png", ITEM_ENTITY_SIZE))
    register_item_data(
        ITEM_TYPE,
        ItemData(ui_icon_sprite, sprite, "Staff of Fire", "Empowers your fireball ability"))
