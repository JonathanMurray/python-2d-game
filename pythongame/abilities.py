from pythongame.common import *
from pythongame.game_data import AOE_PROJECTILE_SIZE
from pythongame.game_state import WorldEntity, Projectile, GameState
from pythongame.projectiles import create_projectile_controller
from pythongame.visual_effects import VisualCircle, VisualLine, VisualRect


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    ability_effects[ability_type](game_state)


def _apply_heal(game_state: GameState):
    game_state.player_state.gain_buff(BuffType.HEALING_OVER_TIME, Millis(3500))


def _apply_aoe_attack(game_state: GameState):
    player_entity = game_state.player_entity
    aoe_center_pos = translate_in_direction(player_entity.get_center_position(), player_entity.direction, 60)
    aoe_pos = get_position_from_center_position(aoe_center_pos, AOE_PROJECTILE_SIZE)
    projectile_speed = 0.07
    entity = WorldEntity(aoe_pos, AOE_PROJECTILE_SIZE, Sprite.WHIRLWIND, player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_AOE))
    game_state.projectile_entities.append(projectile)


def _apply_channel_attack(game_state: GameState):
    game_state.player_state.gain_buff(BuffType.CHANNELING_MAGIC_MISSILES, Millis(1000))


def _apply_teleport(game_state: GameState):
    player_entity = game_state.player_entity
    previous_position = player_entity.get_center_position()
    new_position = translate_in_direction((player_entity.x, player_entity.y), player_entity.direction, 140)
    player_entity.set_position(new_position)
    new_center_position = player_entity.get_center_position()

    color = (140, 140, 230)
    game_state.visual_effects.append(VisualCircle(color, previous_position, 35, Millis(150), 1))
    game_state.visual_effects.append(VisualRect(color, previous_position, 50, Millis(150)))
    game_state.visual_effects.append(VisualLine(color, previous_position, new_center_position, Millis(200), 1))
    game_state.visual_effects.append(VisualCircle(color, new_center_position, 50, Millis(300), 2, player_entity))


ability_effects = {
    AbilityType.HEAL: _apply_heal,
    AbilityType.AOE_ATTACK: _apply_aoe_attack,
    AbilityType.CHANNEL_ATTACK: _apply_channel_attack,
    AbilityType.TELEPORT: _apply_teleport
}


def register_ability_effect(ability_type, effect_function):
    ability_effects[ability_type] = effect_function
