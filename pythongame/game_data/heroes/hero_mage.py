from pythongame.core.common import HeroId, PortraitIconSprite, PLAYER_ENTITY_SIZE, HeroUpgradeId, UiIconSprite, \
    ItemType
from pythongame.core.game_data import Sprite, Direction, AbilityType, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData, register_ui_icon_sprite_path
from pythongame.core.game_state import PlayerLevelBonus
from pythongame.core.item_data import randomized_item_id
from pythongame.core.talents import TalentsConfig, TalentTierConfig, TalentTierOptionConfig
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.abilities.ability_arcane_fire import ARCANE_FIRE_UPGRADED_COOLDOWN, \
    ARCANE_FIRE_UPGRADED_MANA_COST
from pythongame.game_data.abilities.ability_entangling_roots import ENTANGLING_ROOTS_UPGRADED_COOLDOWN
from pythongame.game_data.abilities.ability_fireball import FIREBALL_TALENT_BURN_TOTAL_DAMAGE, \
    FIREBALL_TALENT_BURN_DURATION, FIREBALL_UPGRADED_MANA_COST
from pythongame.game_data.abilities.ability_whirlwind import WHIRLWIND_TALENT_STUN_DURATION
from pythongame.game_data.heroes.generic_talents import TALENT_CHOICE_ARMOR_DAMAGE, TALENT_CHOICE_HEALTH_MANA, \
    TALENT_CHOICE_HEALTH_MANA_REGEN, TALENT_CHOICE_MOVE_SPEED_MAGIC_RESIST

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
    register_ui_icon_sprite_path(UiIconSprite.TALENT_LIGHT_FOOTED, "resources/graphics/boots_of_haste.png")


def _get_initial_player_state_mage() -> InitialPlayerStateData:
    health = 40
    mana = 60
    mana_regen = 3.5
    health_per_level = 5
    mana_per_level = 10
    armor_per_level = 0.3
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level, armor_per_level)
    armor = 1
    dodge_chance = 0.05
    consumable_slots = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.FIREBALL]
    new_level_abilities = {
        2: AbilityType.WHIRLWIND,
        5: AbilityType.ENTANGLING_ROOTS,
        7: AbilityType.ARCANE_FIRE
    }

    talents_state = TalentsConfig(
        {
            3: TALENT_CHOICE_ARMOR_DAMAGE,
            4: TalentTierConfig(
                TalentTierOptionConfig("Raging fire", "Enemies hit by your fireballs take additional " +
                                       str(FIREBALL_TALENT_BURN_TOTAL_DAMAGE) + " damage over " +
                                       "{:.1f}".format(FIREBALL_TALENT_BURN_DURATION / 1000) + "s",
                                       HeroUpgradeId.ABILITY_FIREBALL_BURN, UiIconSprite.ABILITY_FIREBALL),
                TalentTierOptionConfig("Hurricane", "Whirlwind has a chance to stun affected enemies for " +
                                       "{:.1f}".format(WHIRLWIND_TALENT_STUN_DURATION / 1000) + "s",
                                       HeroUpgradeId.ABILITY_WHIRLWIND_STUN, UiIconSprite.ABILITY_WHIRLWIND)),
            5: TALENT_CHOICE_HEALTH_MANA,
            6: TalentTierConfig(
                TalentTierOptionConfig("Swift justice", "Reduces the cooldown of your Entangling Roots ability to " +
                                       "{:.1f}".format(ENTANGLING_ROOTS_UPGRADED_COOLDOWN / 1000) + "s",
                                       HeroUpgradeId.ABILITY_ENTANGLING_ROOTS_COOLDOWN,
                                       UiIconSprite.ABILITY_ENTANGLING_ROOTS),
                TalentTierOptionConfig("Flamethrower", "Reduces the mana-cost of your Fireball ability to " +
                                       str(FIREBALL_UPGRADED_MANA_COST),
                                       HeroUpgradeId.ABILITY_FIREBALL_MANA_COST, UiIconSprite.ABILITY_FIREBALL)),
            7: TALENT_CHOICE_HEALTH_MANA_REGEN,
            8: TalentTierConfig(
                TalentTierOptionConfig("Power hungry",
                                       "Reduces the cooldown of your Arcane Fire ability to " +
                                       "{:.1f}".format(ARCANE_FIRE_UPGRADED_COOLDOWN / 1000) +
                                       "s, but increases its mana-cost to " + str(ARCANE_FIRE_UPGRADED_MANA_COST),
                                       HeroUpgradeId.ABILITY_ARCANE_FIRE_COOLDOWN,
                                       UiIconSprite.ABILITY_ARCANE_FIRE),
                TalentTierOptionConfig("Light-footed", "Lets you keep moving while casting Fireball and Whirlwind",
                                       HeroUpgradeId.MAGE_LIGHT_FOOTED, UiIconSprite.TALENT_LIGHT_FOOTED)),
            9: TALENT_CHOICE_MOVE_SPEED_MAGIC_RESIST,

        })
    block_chance = 0.1
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, dodge_chance,
        level_bonus, talents_state, block_chance, [randomized_item_id(ItemType.NOVICE_WAND)])
