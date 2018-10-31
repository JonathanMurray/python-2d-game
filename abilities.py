from common import *
from game_data import ATTACK_PROJECTILE_SIZE, AOE_PROJECTILE_SIZE
from game_state import WorldEntity, Projectile
from projectiles import create_projectile_controller

ATTACK_PROJECTILE_SPEED = 8
HEAL_ABILITY_AMOUNT = 10
AOE_PROJECTILE_SPEED = 3


def apply_ability_effect(game_state, ability_type):
    if ability_type == AbilityType.ATTACK:
        _apply_attack(game_state)
    elif ability_type == AbilityType.HEAL:
        _apply_heal(game_state)
    elif ability_type == AbilityType.AOE_ATTACK:
        _apply_aoe_attack(game_state)
    else:
        raise Exception("Unhandled ability type: " + str(ability_type))


def _apply_heal(game_state):
    game_state.player_state.add_buff(BuffType.HEALING_OVER_TIME, 3500)


def _apply_attack(game_state):
    player_center_position = game_state.player_entity.get_center_position()
    projectile_pos = (player_center_position[0] - ATTACK_PROJECTILE_SIZE[0] / 2,
                      player_center_position[1] - ATTACK_PROJECTILE_SIZE[1] / 2)
    entity = WorldEntity(projectile_pos, ATTACK_PROJECTILE_SIZE, Sprite.FIREBALL, game_state.player_entity.direction,
                         ATTACK_PROJECTILE_SPEED)
    projectile = Projectile(entity, True, create_projectile_controller(ProjectileType.PLAYER))
    game_state.projectile_entities.append(projectile)


def _apply_aoe_attack(game_state):
    x, y = game_state.player_entity.get_center_position()
    direction = game_state.player_entity.direction
    distance = 80
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

    entity = WorldEntity(aoe_pos, AOE_PROJECTILE_SIZE, Sprite.WHIRLWIND, game_state.player_entity.direction,
                         AOE_PROJECTILE_SPEED)
    projectile = Projectile(entity, True, create_projectile_controller(ProjectileType.PLAYER_AOE))
    game_state.projectile_entities.append(projectile)
