from typing import Dict

from pythongame.core.common import ItemType
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_portrait_icon_sprite_path, PortraitIconSprite
from pythongame.core.game_state import PlayerState

PLAYER_ENTITY_SIZE = (30, 30)
PLAYER_ENTITY_SPEED = 0.105

# This controls which hero the player will control in the game
hero_choice = 2


def get_initial_player_state() -> PlayerState:
    if hero_choice == 1:
        return _get_initial_player_state_1()
    elif hero_choice == 2:
        return _get_initial_player_state_2()


def register_player_data():
    if hero_choice == 1:
        _register_player_data_1()
    elif hero_choice == 2:
        _register_player_data_2()


def _get_initial_player_state_1() -> PlayerState:
    health = 50
    mana = 120
    mana_regen = 4
    consumable_slots = {
        1: ConsumableType.HEALTH_LESSER,
        2: ConsumableType.MANA_LESSER,
        3: None,
        4: None,
        5: None
    }
    abilities = [AbilityType.FIREBALL]
    items: Dict[int, ItemType] = {
        1: None,
        2: None,
        3: None
    }
    new_level_abilities = {2: AbilityType.WHIRLWIND, 3: AbilityType.ENTANGLING_ROOTS}
    return PlayerState(health, health, mana, mana, mana_regen, consumable_slots, abilities, items, new_level_abilities)


def _get_initial_player_state_2() -> PlayerState:
    health = 75
    mana = 50
    mana_regen = 1
    consumable_slots = {
        1: ConsumableType.MANA_LESSER,
        2: ConsumableType.MANA_LESSER,
        3: None,
        4: None,
        5: None
    }
    abilities = [AbilityType.SWORD_SLASH, AbilityType.BLOOD_LUST, AbilityType.CHARGE]
    items: Dict[int, ItemType] = {
        1: ItemType.WINGED_BOOTS,
        2: None,
        3: None
    }
    new_level_abilities = {}
    return PlayerState(health, health, mana, mana, mana_regen, consumable_slots, abilities, items, new_level_abilities)


def _register_player_data_1():
    player_sprite_sheet = SpriteSheet("resources/graphics/player.gif")
    original_sprite_size = (32, 48)
    scaled_sprite_size = (60, 60)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (3, 0)],
        Direction.LEFT: [(0, 1), (1, 1), (2, 1), (3, 1)],
        Direction.RIGHT: [(0, 2), (1, 2), (2, 2), (3, 2)],
        Direction.UP: [(0, 3), (1, 3), (2, 3), (3, 3)]
    }
    sprite_position_relative_to_entity = (-15, -30)
    register_entity_sprite_map(Sprite.PLAYER, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(PortraitIconSprite.PLAYER, 'resources/graphics/player_portrait.gif')


def _register_player_data_2():
    player_sprite_sheet = SpriteSheet("resources/graphics/hero2.png")
    original_sprite_size = (24, 49)
    scaled_sprite_size = (46, 75)
    indices_by_dir = {
        Direction.DOWN: [(0, 0), (1, 0), (2, 0), (1, 0)],
        Direction.UP: [(0, 1), (1, 1), (2, 1), (1, 1)],
        Direction.LEFT: [(0, 2), (1, 2), (2, 2), (1, 2)],
        Direction.RIGHT: [(0, 3), (1, 3), (2, 3), (1, 3)]
    }
    sprite_position_relative_to_entity = (-8, -45)
    register_entity_sprite_map(Sprite.PLAYER, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(PortraitIconSprite.PLAYER, 'resources/graphics/hero2_portrait.png')
