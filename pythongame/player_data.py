from pythongame.core.game_data import register_directional_entity_sprite_initializers, Sprite, Direction, \
    SpriteInitializer

PLAYER_ENTITY_SIZE = (60, 60)


def register_player_data():
    initializers = {
        Direction.DOWN: SpriteInitializer("resources/player/player_down.png", PLAYER_ENTITY_SIZE),
        Direction.RIGHT: SpriteInitializer("resources/player/player_right.png", PLAYER_ENTITY_SIZE),
        Direction.LEFT: SpriteInitializer("resources/player/player_left.png", PLAYER_ENTITY_SIZE),
        Direction.UP: SpriteInitializer("resources/player/player_up.png", PLAYER_ENTITY_SIZE)
    }
    register_directional_entity_sprite_initializers(Sprite.PLAYER, initializers)
