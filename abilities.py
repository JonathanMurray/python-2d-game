from common import *
from game_state import WorldEntity, Projectile

COLOR_ATTACK_PROJECTILE = (200, 5, 200)
ATTACK_PROJECTILE_SIZE = (25, 25)
ATTACK_PROJECTILE_SPEED = 8

HEAL_ABILITY_AMOUNT = 10

COLOR_AOE_PROJECTILE = (200, 0, 100)
AOE_PROJECTILE_SPEED = 3


def try_use_ability(game_state, ability_type):
    if ability_type == AbilityType.ATTACK:
        _try_use_attack_ability(game_state)
    elif ability_type == AbilityType.HEAL:
        _try_use_heal_ability(game_state)
    elif ability_type == AbilityType.AOE_ATTACK:
        _try_use_aoe_attack_ability(game_state)
    else:
        raise Exception("Unhandled ability type: " + str(ability_type))


def _try_use_heal_ability(game_state):
    mana_cost = ability_mana_costs[AbilityType.HEAL]
    if game_state.player_stats.mana >= mana_cost:
        game_state.player_stats.lose_mana(mana_cost)
        game_state.player_stats.gain_health(HEAL_ABILITY_AMOUNT)


def _try_use_attack_ability(game_state):
    mana_cost = ability_mana_costs[AbilityType.ATTACK]
    if game_state.player_stats.mana >= mana_cost:
        game_state.player_stats.lose_mana(mana_cost)
        proj_pos = (game_state.player_entity.get_center_x() - ATTACK_PROJECTILE_SIZE[0] / 2,
                    game_state.player_entity.get_center_y() - ATTACK_PROJECTILE_SIZE[1] / 2)
        entity = WorldEntity(proj_pos, ATTACK_PROJECTILE_SIZE,
                             COLOR_ATTACK_PROJECTILE, game_state.player_entity.direction,
                             ATTACK_PROJECTILE_SPEED, ATTACK_PROJECTILE_SPEED)
        game_state.projectile_entities.append(Projectile(entity, 0, 3000))


def _try_use_aoe_attack_ability(game_state):
    mana_cost = ability_mana_costs[AbilityType.HEAL]
    if game_state.player_stats.mana >= mana_cost:
        game_state.player_stats.lose_mana(mana_cost)
        direction = game_state.player_entity.direction
        x = game_state.player_entity.get_center_x()
        y = game_state.player_entity.get_center_y()
        box_w = 130
        distance = 150
        if direction == Direction.RIGHT:
            aoe_pos = (x + distance - box_w / 2, y - box_w / 2)
        elif direction == Direction.DOWN:
            aoe_pos = (x - box_w / 2, y + distance - box_w / 2)
        elif direction == Direction.LEFT:
            aoe_pos = (x - distance - box_w / 2, y - box_w / 2)
        elif direction == Direction.UP:
            aoe_pos = (x - box_w / 2, y - distance - box_w / 2)

        entity = WorldEntity(aoe_pos, (box_w, box_w), COLOR_AOE_PROJECTILE,
                             game_state.player_entity.direction, AOE_PROJECTILE_SPEED, AOE_PROJECTILE_SPEED)
        game_state.projectile_entities.append(Projectile(entity, 250, 650))
