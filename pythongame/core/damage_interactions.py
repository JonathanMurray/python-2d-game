from pythongame.core.enemy_target_selection import EnemyTarget
from pythongame.core.game_state import NonPlayerCharacter, GameState
from pythongame.core.visual_effects import create_visual_damage_text


# Returns
# True if damage was dealt.
# False if enemy was invulnerable.
def deal_player_damage_to_enemy(game_state: GameState, npc: NonPlayerCharacter, amount: int):
    if npc.invulnerable:
        return False
    npc.lose_health(amount)
    game_state.visual_effects.append(create_visual_damage_text(npc.world_entity, amount))
    health_from_life_steal = game_state.player_state.life_steal_ratio * float(amount)
    game_state.player_state.gain_health(health_from_life_steal)
    return True


def deal_damage_to_player(game_state: GameState, amount: float):
    game_state.player_state.lose_health(amount)
    rounded_amount = round(amount)
    if rounded_amount > 0:
        game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, rounded_amount))


def deal_npc_damage_to_npc(game_state: GameState, target: NonPlayerCharacter, amount: float):
    target.lose_health(amount)
    rounded_amount = round(amount)
    if rounded_amount > 0:
        game_state.visual_effects.append(create_visual_damage_text(target.world_entity, rounded_amount))


def deal_npc_damage(damage_amount: float, game_state: GameState, target: EnemyTarget):
    if target.non_enemy_npc:
        deal_npc_damage_to_npc(game_state, target.non_enemy_npc, damage_amount)
    else:
        deal_damage_to_player(game_state, damage_amount)
