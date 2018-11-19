from pythongame.core.game_data import Sprite, Direction, PotionType, AbilityType, SpriteSheet, \
    register_entity_sprite_map
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
    player_sprite_sheet = SpriteSheet("resources/graphics/player.gif")
    original_sprite_size = (32, 48)
    scaled_sprite_size = PLAYER_ENTITY_SIZE
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1), (3, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2), (3, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3), (3, 3)]
    }
    register_entity_sprite_map(Sprite.PLAYER, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir)
