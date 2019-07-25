from typing import Dict

from pythongame.core.common import ItemType, HeroId, PortraitIconSprite
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData
from pythongame.core.game_state import PlayerLevelBonus


def register_hero_warrior():
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
    entity_speed = 0.105
    entity_size = (30, 30)
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_warrior(), entity_speed, entity_size)
    register_hero_data(HeroId.WARRIOR, hero_data)


def _get_initial_player_state_warrior() -> InitialPlayerStateData:
    health = 60
    mana = 40
    mana_regen = 1
    health_per_level = 15
    mana_per_level = 5
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level)
    armor = 2
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
        3: None,
        4: None,
        5: None,
        6: None
    }
    new_level_abilities = {
        3: AbilityType.CHARGE,
        5: AbilityType.BLOOD_LUST,
        7: AbilityType.STOMP
    }
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, items, new_level_abilities, HeroId.WARRIOR, armor,
        level_bonus)
