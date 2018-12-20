import pygame

from pythongame.core.common import ItemType
from pythongame.core.game_data import Sprite, Direction, PotionType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_user_ability_key, UserAbilityKey
from pythongame.core.game_state import PlayerState

PLAYER_ENTITY_SIZE = (40, 30)
PLAYER_ENTITY_SPEED = 0.1

_player_potion_slots = {
    1: PotionType.HEALTH,
    2: None,
    3: None,
    4: None,
    5: None
}

_abilities = [AbilityType.FIREBALL, AbilityType.FROST_NOVA, AbilityType.WHIRLWIND, AbilityType.ENTANGLING_ROOTS]
register_user_ability_key(AbilityType.FIREBALL, UserAbilityKey("Q", pygame.K_q))
register_user_ability_key(AbilityType.FROST_NOVA, UserAbilityKey("W", pygame.K_w))
register_user_ability_key(AbilityType.WHIRLWIND, UserAbilityKey("E", pygame.K_e))
register_user_ability_key(AbilityType.ENTANGLING_ROOTS, UserAbilityKey("R", pygame.K_r))
health = 50
mana = 100
max_mana = 150
mana_regen = 0.0028
_items = {
    1: ItemType.WINGED_BOOTS,
    2: None,
    3: None
}
INTIAL_PLAYER_STATE = PlayerState(health, health, mana, max_mana, mana_regen, _player_potion_slots, _abilities, _items)


def register_player_data():
    player_sprite_sheet = SpriteSheet("resources/graphics/player.gif")
    original_sprite_size = (32, 48)
    scaled_sprite_size = (60, 60)
    sprite_position_relative_to_entity = (-10, -30)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1), (3, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2), (3, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3), (3, 3)]
    }
    register_entity_sprite_map(Sprite.PLAYER, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
