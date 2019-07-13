from typing import Dict

from pythongame.core.common import ItemType, HeroId
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_portrait_icon_sprite_path, PortraitIconSprite, register_hero_data, HeroData, \
    InitialPlayerStateData

PLAYER_ENTITY_SIZE = (30, 30)
PLAYER_ENTITY_SPEED = 0.105


# TODO Split up hero definitions into separate files

def register_player_data():
    _register_player_data_mage()
    _register_player_data_warrior()


def _get_initial_player_state_mage() -> InitialPlayerStateData:
    health = 40
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
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, items, new_level_abilities, HeroId.MAGE)


def _get_initial_player_state_warrior() -> InitialPlayerStateData:
    health = 75
    mana = 50
    mana_regen = 1
    consumable_slots = {
        1: ConsumableType.HEALTH_LESSER,
        2: ConsumableType.HEALTH_LESSER,
        3: None,
        4: None,
        5: None
    }
    abilities = [AbilityType.SWORD_SLASH]
    items: Dict[int, ItemType] = {
        1: ItemType.WINGED_BOOTS,
        2: None,
        3: None
    }
    new_level_abilities = {2: AbilityType.CHARGE, 3: AbilityType.BLOOD_LUST}
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, items, new_level_abilities, HeroId.WARRIOR)


def _register_player_data_mage():
    sprite = Sprite.HERO_MAGE
    portrait_icon_sprite = PortraitIconSprite.HERO_MAGE
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
    register_entity_sprite_map(sprite, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/player_portrait.gif')
    register_hero_data(HeroId.MAGE, HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_mage()))


def _register_player_data_warrior():
    sprite = Sprite.HERO_WARRIOR
    portrait_icon_sprite = PortraitIconSprite.HERO_WARRIOR
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
    register_entity_sprite_map(sprite, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/hero2_portrait.png')
    register_hero_data(HeroId.WARRIOR, HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_warrior()))
