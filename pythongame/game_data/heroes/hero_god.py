from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityWasUsedSuccessfully, AbilityResult
from pythongame.core.common import HeroId, PortraitIconSprite, UiIconSprite, Millis, PLAYER_ENTITY_SIZE
from pythongame.core.game_data import Sprite, Direction, AbilityType, register_entity_sprite_map, \
    register_portrait_icon_sprite_path, register_hero_data, HeroData, \
    InitialPlayerStateData, register_ui_icon_sprite_path
from pythongame.core.game_state import PlayerLevelBonus, GameState
from pythongame.core.talents import TalentsConfig
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.game_data.heroes.generic_talents import TALENT_CHOICE_ARMOR_DAMAGE

HERO_ID = HeroId.GOD


def register_hero_god():
    sprite = Sprite.HERO_GOD
    portrait_icon_sprite = PortraitIconSprite.HERO_GOD
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
    entity_speed = 0.5
    hero_data = HeroData(sprite, portrait_icon_sprite, _get_initial_player_state_god(), entity_speed,
                         PLAYER_ENTITY_SIZE, "God mode...")
    register_hero_data(HERO_ID, hero_data)
    _register_kill_everything_ability()


def _get_initial_player_state_god() -> InitialPlayerStateData:
    health = 9999
    mana = 9999
    mana_regen = 100
    level_bonus = PlayerLevelBonus(0, 0, 0)
    armor = 99
    dodge_chance = 0.05
    consumable_slots = {
        1: [],
        2: [],
        3: [],
        4: [],
        5: []
    }
    abilities = [AbilityType.KILL_EVERYTHING, AbilityType.TELEPORT]
    new_level_abilities = {}
    talents_state = TalentsConfig({
        2: TALENT_CHOICE_ARMOR_DAMAGE
    })
    block_chance = 0
    return InitialPlayerStateData(
        health, mana, mana_regen, consumable_slots, abilities, new_level_abilities, HERO_ID, armor, dodge_chance,
        level_bonus, talents_state, block_chance, [])


def _apply_ability(game_state: GameState) -> AbilityResult:
    player_entity = game_state.game_world.player_entity
    for enemy in game_state.game_world.get_enemies_within_x_y_distance_of(400, player_entity.get_center_position()):
        enemy.health_resource.set_zero()
    return AbilityWasUsedSuccessfully()


def _register_kill_everything_ability():
    ability_type = AbilityType.KILL_EVERYTHING
    ui_icon_sprite = UiIconSprite.ABILITY_KILL_EVERYTHING
    mana_cost = 1
    cooldown = Millis(500)

    register_ability_effect(ability_type, _apply_ability)
    description = "Kill all nearby enemies"
    ability_data = AbilityData("Kill everything", ui_icon_sprite, mana_cost, cooldown, description, None)
    register_ability_data(ability_type, ability_data)
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/whirlwind.png")
