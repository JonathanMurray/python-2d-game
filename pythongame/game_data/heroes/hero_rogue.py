from pythongame.core.common import HeroId, PortraitIconSprite, PLAYER_ENTITY_SIZE
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, SpriteSheet, \
    register_entity_sprite_map, register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData
from pythongame.core.game_state import PlayerLevelBonus

HERO_ID = HeroId.ROGUE


def register_hero_rogue():
    sprite = Sprite.HERO_ROGUE
    portrait_icon_sprite = PortraitIconSprite.HERO_ROGUE
    player_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 0
    indices_by_dir = {
        Direction.DOWN: [(x + i, 4) for i in range(3)],
        Direction.LEFT: [(x + i, 5) for i in range(3)],
        Direction.RIGHT: [(x + i, 6) for i in range(3)],
        Direction.UP: [(x + i, 7) for i in range(3)]
    }
    sprite_position_relative_to_entity = (-8, -16)
    register_entity_sprite_map(sprite, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/portrait_rogue_hero.png')
    entity_speed = 0.105
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_rogue(), entity_speed,
                         PLAYER_ENTITY_SIZE)
    register_hero_data(HERO_ID, hero_data)


def _get_initial_player_state_rogue() -> InitialPlayerStateData:
    health = 50
    mana = 50
    mana_regen = 2.5
    health_per_level = 10
    mana_per_level = 10
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level)
    armor = 2
    consumable_slots = {
        1: [ConsumableType.HEALTH_LESSER],
        2: [ConsumableType.HEALTH_LESSER],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.SHIV]
    new_level_abilities = {
        3: AbilityType.SNEAK,
        5: AbilityType.DASH,
        7: AbilityType.INFUSE_DAGGER
    }
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, level_bonus)
