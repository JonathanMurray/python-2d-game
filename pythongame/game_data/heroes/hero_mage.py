from pythongame.core.common import HeroId, PortraitIconSprite, PLAYER_ENTITY_SIZE, HeroUpgrade, UiIconSprite
from pythongame.core.game_data import Sprite, Direction, ConsumableType, AbilityType, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData
from pythongame.core.game_state import PlayerLevelBonus
from pythongame.core.image_loading import SpriteSheet
from pythongame.core.talents import TalentsState, TalentChoice, TalentChoiceOption
from pythongame.game_data.heroes.generic_talents import GENERIC_TALENT_CHOICE

HERO_ID = HeroId.MAGE


def register_hero_mage():
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
    entity_speed = 0.105
    description = "A ranged spellcaster that is explosive but fragile, the mage can take down " \
                  "large groups of enemies effectively, as long as she can keep her distance..."
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_mage(), entity_speed,
                         PLAYER_ENTITY_SIZE, description)
    register_hero_data(HERO_ID, hero_data)


def _get_initial_player_state_mage() -> InitialPlayerStateData:
    health = 40
    mana = 60
    mana_regen = 3.5
    health_per_level = 5
    mana_per_level = 10
    armor_per_level = 0
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level, armor_per_level)
    armor = 1
    consumable_slots = {
        1: [ConsumableType.HEALTH_LESSER],
        2: [ConsumableType.MANA_LESSER],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.FIREBALL]
    new_level_abilities = {
        3: AbilityType.WHIRLWIND,
        5: AbilityType.ENTANGLING_ROOTS,
        7: AbilityType.CHANNEL_ATTACK
    }
    # TODO Add more talents (unique to this hero)
    talents_state = TalentsState({
        2: GENERIC_TALENT_CHOICE,
        4: TalentChoice(TalentChoiceOption("Burn", "Enemies hit by your fireballs take additional damage over time",
                                           HeroUpgrade.ABILITY_FIREBALL_BURN, UiIconSprite.ABILITY_FIREBALL),
                        TalentChoiceOption("Stun", "Whirlwind periodically stuns enemies it hits for a short moment",
                                           HeroUpgrade.ABILITY_WHIRLWIND_STUN, UiIconSprite.ABILITY_WHIRLWIND)),
        6: TalentChoice(TalentChoiceOption("Quick", "Reduces the cooldown of your root ability",
                                           HeroUpgrade.ABILITY_ENTANGLING_ROOTS_COOLDOWN,
                                           UiIconSprite.ABILITY_ENTANGLING_ROOTS),
                        TalentChoiceOption("Cheap", "Reduces the mana-cost of your fireball ability",
                                           HeroUpgrade.ABILITY_FIREBALL_MANA_COST,
                                           UiIconSprite.ABILITY_FIREBALL))
    })
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, level_bonus,
        talents_state)
