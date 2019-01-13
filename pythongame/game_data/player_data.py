from typing import Dict

from pythongame.core.ability_learning import USER_ABILITY_KEYS
from pythongame.core.common import ItemType
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_user_ability_key
from pythongame.core.game_state import PlayerState

PLAYER_ENTITY_SIZE = (30, 30)
PLAYER_ENTITY_SPEED = 0.105

_player_consumable_slots = {
    1: ConsumableType.HEALTH_LESSER,
    2: ConsumableType.MANA_LESSER,
    3: None,
    4: None,
    5: None
}

_abilities = [AbilityType.FIREBALL,
              AbilityType.WHIRLWIND,
              AbilityType.ENTANGLING_ROOTS]

for ability_type, user_ability_key in zip(_abilities, USER_ABILITY_KEYS):
    register_user_ability_key(ability_type, user_ability_key)

health = 50
mana = 100
max_mana = 120
mana_regen = 4
_items: Dict[int, ItemType] = {
    1: None,
    2: None,
    3: None
}
INTIAL_PLAYER_STATE = PlayerState(health, health, mana, max_mana, mana_regen, _player_consumable_slots, _abilities, _items)


def register_player_data():
    player_sprite_sheet = SpriteSheet("resources/graphics/player.gif")
    original_sprite_size = (32, 48)
    scaled_sprite_size = (60, 60)
    sprite_position_relative_to_entity = (-15, -30)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1), (3, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2), (3, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3), (3, 3)]
    }
    register_entity_sprite_map(Sprite.PLAYER, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
