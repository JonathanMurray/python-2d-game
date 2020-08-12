from pythongame.core.game_data import Sprite, register_entity_sprite_initializer
from pythongame.core.view.image_loading import SpriteInitializer

DUNGEON_ENTRANCE_ENTITY_SIZE = (35, 25)


def register_dungeon_entrance():
    register_entity_sprite_initializer(Sprite.DUNGEON_ENTRANCE,
                                       SpriteInitializer("resources/graphics/wall_lightpole.png", (35, 105)), (0, -80))
