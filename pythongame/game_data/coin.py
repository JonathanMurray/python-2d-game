from pythongame.core.common import Sprite
from pythongame.core.game_data import register_entity_sprite_initializer
from pythongame.core.view.image_loading import SpriteInitializer


def register_coin():
    register_entity_sprite_initializer(
        Sprite.COINS_1, SpriteInitializer("resources/graphics/coins_1.png", (22, 17)))
    register_entity_sprite_initializer(
        Sprite.COINS_2, SpriteInitializer("resources/graphics/coins_2.png", (32, 26)))
    register_entity_sprite_initializer(
        Sprite.COINS_5, SpriteInitializer("resources/graphics/coins_5.png", (30, 30)))
