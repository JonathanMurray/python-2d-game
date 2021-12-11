from pythongame.core.buff_effects import register_buff_effect, StatModifyingBuffEffect, get_buff_effect
from pythongame.core.common import HeroId, PortraitIconSprite, PLAYER_ENTITY_SIZE, HeroUpgradeId, UiIconSprite, \
    ItemType, \
    HeroStat, BuffType, Millis
from pythongame.core.game_data import Sprite, Direction, AbilityType, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData, register_buff_text
from pythongame.core.game_state import PlayerLevelBonus, GameState, Event, PlayerBlockedEvent
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, HeroUpgrade, AbstractHeroUpgradeEffect
from pythongame.core.item_data import randomized_item_id
from pythongame.core.talents import TalentsConfig, TalentTierConfig, TalentTierOptionConfig
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.abilities.ability_bloodlust import BLOODLUST_UPGRADED_INCREASED_DURATION_FROM_KILL
from pythongame.game_data.abilities.ability_sword_slash import ABILITY_SLASH_UPGRADED_COOLDOWN
from pythongame.game_data.heroes.generic_talents import TALENT_CHOICE_ARMOR_DAMAGE, TALENT_CHOICE_HEALTH_MANA, \
    TALENT_CHOICE_HEALTH_MANA_REGEN, TALENT_CHOICE_MOVE_SPEED_MAGIC_RESIST

HERO_ID = HeroId.WARRIOR

BUFF_RETRIBUTION = BuffType.BUFFED_FROM_RETRIBUTION_TALENT
BUFF_RETRIBUTION_DURATION = Millis(2000)
BUFF_RETRIBUTION_BONUS_BLOCK_CHANCE = 0.05
BUFF_RETRIBUTION_BONUS_DAMAGE = 0.4


def register_hero_warrior():
    sprite = Sprite.HERO_WARRIOR
    portrait_icon_sprite = PortraitIconSprite.HERO_WARRIOR
    player_sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x + i, 4) for i in range(3)],
        Direction.LEFT: [(x + i, 5) for i in range(3)],
        Direction.RIGHT: [(x + i, 6) for i in range(3)],
        Direction.UP: [(x + i, 7) for i in range(3)]
    }
    sprite_position_relative_to_entity = (-8, -16)
    register_entity_sprite_map(sprite, player_sprite_sheet, original_sprite_size,
                               scaled_sprite_size, indices_by_dir, sprite_position_relative_to_entity)
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/portrait_warrior_hero.png')
    entity_speed = 0.105
    description = "A sturdy melee fighter, the warrior can stand his ground against any foe, and thrives when there " \
                  "are enemies all around."
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_warrior(), entity_speed,
                         PLAYER_ENTITY_SIZE, description)
    register_hero_data(HERO_ID, hero_data)
    register_hero_upgrade_effect(HeroUpgradeId.WARRIOR_RETRIBUTION, UpgradeRetribution())
    register_buff_effect(BUFF_RETRIBUTION, BuffedFromRetribution)
    register_buff_text(BUFF_RETRIBUTION, "Retribution")


class UpgradeRetribution(AbstractHeroUpgradeEffect):
    def apply(self, game_state: GameState):
        game_state.player_state.modify_stat(HeroStat.BLOCK_CHANCE, BUFF_RETRIBUTION_BONUS_BLOCK_CHANCE)

    def revert(self, game_state: GameState):
        game_state.player_state.modify_stat(HeroStat.BLOCK_CHANCE, -BUFF_RETRIBUTION_BONUS_BLOCK_CHANCE)


class BuffedFromRetribution(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_RETRIBUTION, {HeroStat.DAMAGE: BUFF_RETRIBUTION_BONUS_DAMAGE})


class RetributionHeroUpgrade(HeroUpgrade):

    def handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_RETRIBUTION), BUFF_RETRIBUTION_DURATION)


def _get_initial_player_state_warrior() -> InitialPlayerStateData:
    health = 60
    mana = 30
    mana_regen = 2
    health_per_level = 15
    mana_per_level = 5
    armor_per_level = 1
    level_bonus = PlayerLevelBonus(health_per_level, mana_per_level, armor_per_level)
    armor = 3
    dodge_chance = 0.05
    consumable_slots = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.SWORD_SLASH]
    new_level_abilities = {
        2: AbilityType.CHARGE,
        5: AbilityType.BLOOD_LUST,
        7: AbilityType.STOMP
    }

    talents_state = TalentsConfig({
        3: TALENT_CHOICE_ARMOR_DAMAGE,
        4: TalentTierConfig(
            TalentTierOptionConfig("Close combat",
                                   "Your Charge ability deals full damage even when used at close range",
                                   HeroUpgradeId.ABILITY_CHARGE_MELEE,
                                   UiIconSprite.ABILITY_CHARGE),
            TalentTierOptionConfig("Brawl",
                                   "Your Slash ability deals max damage if at least 2 enemies are hit",
                                   HeroUpgradeId.ABILITY_SLASH_AOE_BONUS_DAMAGE,
                                   UiIconSprite.ABILITY_SWORD_SLASH)),
        5: TALENT_CHOICE_HEALTH_MANA,
        6: TalentTierConfig(
            TalentTierOptionConfig("Bloodthirst",
                                   "The duration of your Bloodlust ability is now increased by " +
                                   "{:.1f}".format(
                                       BLOODLUST_UPGRADED_INCREASED_DURATION_FROM_KILL / 1000) + "s on kills",
                                   HeroUpgradeId.ABILITY_BLOODLUST_DURATION,
                                   UiIconSprite.ABILITY_BLOODLUST),
            TalentTierOptionConfig("Berserker",
                                   "Reduces the cooldown of your Slash ability to " +
                                   "{:.1f}".format(ABILITY_SLASH_UPGRADED_COOLDOWN / 1000) + "s",
                                   HeroUpgradeId.ABILITY_SLASH_CD,
                                   UiIconSprite.ABILITY_SWORD_SLASH)),
        7: TALENT_CHOICE_HEALTH_MANA_REGEN,
        8: TalentTierConfig(
            TalentTierOptionConfig("Juggernaut",
                                   "Hitting an enemy with your Charge ability resets the cooldown of War Stomp",
                                   HeroUpgradeId.ABILITY_CHARGE_RESET_STOMP_COOLDOWN,
                                   UiIconSprite.ABILITY_STOMP),
            TalentTierOptionConfig("Retribution",
                                   "Increases your block chance by " +
                                   str(int(BUFF_RETRIBUTION_BONUS_BLOCK_CHANCE * 100)) +
                                   "%. Blocking an enemy attack gives +" +
                                   str(int(BUFF_RETRIBUTION_BONUS_DAMAGE * 100)) +
                                   " attack power for " + "{:.1f}".format(BUFF_RETRIBUTION_DURATION / 1000) + "s",
                                   RetributionHeroUpgrade(HeroUpgradeId.WARRIOR_RETRIBUTION),
                                   UiIconSprite.ITEM_SKULL_SHIELD)),
        9: TALENT_CHOICE_MOVE_SPEED_MAGIC_RESIST,
    })
    block_chance = 0.2
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, dodge_chance,
        level_bonus, talents_state, block_chance, [randomized_item_id(ItemType.PRACTICE_SWORD),
                                                   randomized_item_id(ItemType.WOODEN_SHIELD)])
