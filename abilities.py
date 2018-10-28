from common import *
from game_data import ATTACK_PROJECTILE_SIZE, AOE_PROJECTILE_SIZE, ABILITIES
from game_state import WorldEntity, Projectile

ATTACK_PROJECTILE_SPEED = 8
HEAL_ABILITY_AMOUNT = 10
AOE_PROJECTILE_SPEED = 3


def try_use_ability(game_state, ability_type):
    mana_cost = ABILITIES[ability_type].mana_cost
    if game_state.player_state.mana >= mana_cost:
        game_state.player_state.lose_mana(mana_cost)
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
    projectile_pos = (game_state.player_entity.get_center_x() - ATTACK_PROJECTILE_SIZE[0] / 2,
                      game_state.player_entity.get_center_y() - ATTACK_PROJECTILE_SIZE[1] / 2)
    entity = WorldEntity(projectile_pos, ATTACK_PROJECTILE_SIZE, Sprite.FIREBALL, game_state.player_entity.direction,
                         ATTACK_PROJECTILE_SPEED, ATTACK_PROJECTILE_SPEED)
    game_state.projectile_entities.append(Projectile(entity, 0, 3000))


def _apply_aoe_attack(game_state):
    direction = game_state.player_entity.direction
    x = game_state.player_entity.get_center_x()
    y = game_state.player_entity.get_center_y()
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
                         AOE_PROJECTILE_SPEED, AOE_PROJECTILE_SPEED)
    game_state.projectile_entities.append(Projectile(entity, 250, 500))
