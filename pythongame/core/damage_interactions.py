from pythongame.core.game_state import Enemy, GameState
from pythongame.core.visual_effects import create_visual_damage_text


# Returns
# True if damage was dealt.
# False if enemy was invulnerable.
def deal_player_damage_to_enemy(game_state: GameState, enemy: Enemy, amount: int):
    if enemy.invulnerable:
        return False
    enemy.lose_health(amount)
    game_state.visual_effects.append(create_visual_damage_text(enemy.world_entity, amount))
    health_from_life_steal = game_state.player_state.life_steal_ratio * float(amount)
    game_state.player_state.gain_health(health_from_life_steal)
    return True


def deal_damage_to_player(game_state: GameState, amount: float):
    game_state.player_state.lose_health(amount)
    rounded_amount = round(amount)
    if rounded_amount > 0:
        game_state.visual_effects.append(create_visual_damage_text(game_state.player_entity, rounded_amount))
