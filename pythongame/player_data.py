from pythongame.core.game_data import register_directional_entity_sprite_initializers, Sprite, Direction, \
    SpriteInitializer, PotionType, AbilityType
from pythongame.core.game_state import PlayerState

PLAYER_ENTITY_SIZE = (60, 60)

_player_potion_slots = {
    1: PotionType.SPEED,
    2: PotionType.MANA,
    3: PotionType.HEALTH,
    4: PotionType.INVISIBILITY,
    5: PotionType.INVISIBILITY
}

_abilities = [AbilityType.ATTACK, AbilityType.HEAL, AbilityType.AOE_ATTACK, AbilityType.CHANNEL_ATTACK,
              AbilityType.TELEPORT]
INTIAL_PLAYER_STATE = PlayerState(300, 300, 90, 100, 0.002, _player_potion_slots, _abilities)


def register_player_data():
    initializers = {
        Direction.DOWN: SpriteInitializer("resources/player/player_down.png", PLAYER_ENTITY_SIZE),
        Direction.RIGHT: SpriteInitializer("resources/player/player_right.png", PLAYER_ENTITY_SIZE),
        Direction.LEFT: SpriteInitializer("resources/player/player_left.png", PLAYER_ENTITY_SIZE),
        Direction.UP: SpriteInitializer("resources/player/player_up.png", PLAYER_ENTITY_SIZE)
    }
    register_directional_entity_sprite_initializers(Sprite.PLAYER, initializers)
