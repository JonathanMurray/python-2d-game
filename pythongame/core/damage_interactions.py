from pythongame.core.game_state import Enemy, GameState
from pythongame.core.visual_effects import create_visual_damage_text


def deal_player_damage_to_enemy(game_state: GameState, enemy: Enemy, amount: int):
    enemy.lose_health(amount)
    game_state.visual_effects.append(create_visual_damage_text(enemy.world_entity, amount))
    health_from_life_steal = game_state.player_state.life_steal_ratio * float(amount)
    game_state.player_state.gain_health(health_from_life_steal)

# TODO Add method handling enemy -> player

# TODO Handle invulnerability in this package?