from pythongame.common import *
from pythongame.game_data import ATTACK_PROJECTILE_SIZE, AOE_PROJECTILE_SIZE
from pythongame.game_state import WorldEntity, Projectile, GameState
from pythongame.projectiles import create_projectile_controller
from pythongame.visual_effects import VisualCircle, VisualLine, VisualRect


def apply_ability_effect(game_state: GameState, ability_type: AbilityType):
    if ability_type == AbilityType.ATTACK:
        _apply_attack(game_state)
    elif ability_type == AbilityType.HEAL:
        _apply_heal(game_state)
    elif ability_type == AbilityType.AOE_ATTACK:
        _apply_aoe_attack(game_state)
    elif ability_type == AbilityType.CHANNEL_ATTACK:
        _apply_channel_attack(game_state)
    elif ability_type == AbilityType.TELEPORT:
        _apply_teleport(game_state)
    else:
        raise Exception("Unhandled ability type: " + str(ability_type))


def _apply_heal(game_state: GameState):
    game_state.player_state.gain_buff(BuffType.HEALING_OVER_TIME, Millis(3500))


def _apply_attack(game_state: GameState):
    player_center_position = game_state.player_entity.get_center_position()
    projectile_pos = (player_center_position[0] - ATTACK_PROJECTILE_SIZE[0] / 2,
                      player_center_position[1] - ATTACK_PROJECTILE_SIZE[1] / 2)
    entity = WorldEntity(projectile_pos, ATTACK_PROJECTILE_SIZE, Sprite.FIREBALL, game_state.player_entity.direction,
                         0.3)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER))
    game_state.projectile_entities.append(projectile)


def _apply_aoe_attack(game_state: GameState):
    x, y = game_state.player_entity.get_center_position()
    direction = game_state.player_entity.direction
    distance = 60
    if direction == Direction.RIGHT:
        aoe_pos = (x + distance - AOE_PROJECTILE_SIZE[0] / 2, y - AOE_PROJECTILE_SIZE[1] / 2)
    elif direction == Direction.DOWN:
        aoe_pos = (x - AOE_PROJECTILE_SIZE[0] / 2, y + distance - AOE_PROJECTILE_SIZE[1] / 2)
    elif direction == Direction.LEFT:
        aoe_pos = (x - distance - AOE_PROJECTILE_SIZE[0] / 2, y - AOE_PROJECTILE_SIZE[1] / 2)
    elif direction == Direction.UP:
        aoe_pos = (x - AOE_PROJECTILE_SIZE[0] / 2, y - distance - AOE_PROJECTILE_SIZE[1] / 2)
    else:
        raise Exception("Unhandled direction: " + str(direction))

    projectile_speed = 0.07
    entity = WorldEntity(aoe_pos, AOE_PROJECTILE_SIZE, Sprite.WHIRLWIND, game_state.player_entity.direction,
                         projectile_speed)
    projectile = Projectile(entity, create_projectile_controller(ProjectileType.PLAYER_AOE))
    game_state.projectile_entities.append(projectile)


def _apply_channel_attack(game_state: GameState):
    game_state.player_state.gain_buff(BuffType.CHANNELING_MAGIC_MISSILES, Millis(1000))


def _apply_teleport(game_state: GameState):
    direction = game_state.player_entity.direction
    previous_position = game_state.player_entity.get_center_position()

    # TODO Extract this "move distance in given direction" and re-use
    distance = 140
    color = (140, 140, 230)
    game_state.visual_effects.append(VisualCircle(color, previous_position, 35, Millis(150), 1))
    game_state.visual_effects.append(VisualRect(color, previous_position, 50, Millis(150)))
    if direction == Direction.RIGHT:
        game_state.player_entity.x += distance
    elif direction == Direction.DOWN:
        game_state.player_entity.y += distance
    elif direction == Direction.LEFT:
        game_state.player_entity.x -= distance
    elif direction == Direction.UP:
        game_state.player_entity.y -= distance
    else:
        raise Exception("Unhandled direction: " + str(direction))
    new_position = game_state.player_entity.get_center_position()
    game_state.visual_effects.append(VisualLine(color, previous_position, new_position, Millis(200), 1))
    game_state.visual_effects.append(VisualCircle(color, new_position,
                                                  50, Millis(300), 2, game_state.player_entity))
