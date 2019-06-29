from pythongame.core.common import Sprite
from pythongame.core.game_data import register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE


def register_coin():
    register_entity_sprite_initializer(
        Sprite.COIN, SpriteInitializer("resources/graphics/coins.png", ITEM_ENTITY_SIZE))
