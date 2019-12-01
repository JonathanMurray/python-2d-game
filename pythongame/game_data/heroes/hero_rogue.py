from pythongame.core.common import HeroId, PortraitIconSprite, PLAYER_ENTITY_SIZE, HeroUpgrade, UiIconSprite
from pythongame.core.game_data import Sprite, Direction, AbilityType, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData
from pythongame.core.game_state import PlayerLevelBonus
from pythongame.core.talents import TalentsConfig, TalentTierConfig, TalentTierOptionConfig
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.heroes.generic_talents import TALENT_CHOICE_ARMOR_DAMAGE, TALENT_CHOICE_HEALTH_MANA, \
    TALENT_CHOICE_HEALTH_MANA_REGEN

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
    description = "A flexible melee assassin, the rogue can dish out large amounts of damage and is especially " \
                  "effective at singling out powerful enemies."
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_rogue(), entity_speed,
                         PLAYER_ENTITY_SIZE, description)
    register_hero_data(HERO_ID, hero_data)


def _get_initial_player_state_rogue() -> InitialPlayerStateData:
    health = 50
    mana = 50
    mana_regen = 2.5
    health_per_level = 10
    mana_per_level = 10
    armor_per_level = 1
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level, armor_per_level)
    armor = 2
    dodge_chance = 0.1
    consumable_slots = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.SHIV]
    new_level_abilities = {
        2: AbilityType.STEALTH,
        5: AbilityType.DASH,
        7: AbilityType.INFUSE_DAGGER
    }

    talents_state = TalentsConfig({
        3: TALENT_CHOICE_ARMOR_DAMAGE,
        4: TalentTierConfig(TalentTierOptionConfig("Cheap", "Reduces the mana-cost of your stealth ability",
                                                   HeroUpgrade.ABILITY_STEALTH_MANA_COST, UiIconSprite.ABILITY_STEALTH),
                            TalentTierOptionConfig("Stealth",
                                                   "Increases the damage bonus that shiv gets from being used from stealth",
                                                   HeroUpgrade.ABILITY_SHIV_SNEAK_BONUS_DAMAGE,
                                                   UiIconSprite.ABILITY_SHIV)),
        5: TALENT_CHOICE_HEALTH_MANA,
        6: TalentTierConfig(
            TalentTierOptionConfig("Reset",
                                   "The cooldown and mana-cost of your dash ability is reset if it kills an enemy",
                                   HeroUpgrade.ABILITY_DASH_KILL_RESET, UiIconSprite.ABILITY_DASH),
            TalentTierOptionConfig("Init",
                                   "Shiv deals bonus damage on enemies that are at full health, unless you're stealthed",
                                   HeroUpgrade.ABILITY_SHIV_FULL_HEALTH_BONUS_DAMAGE,
                                   UiIconSprite.ABILITY_SHIV)),
        7: TALENT_CHOICE_HEALTH_MANA_REGEN
    })
    block_chance = 0.15
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, dodge_chance,
        level_bonus, talents_state, block_chance)
