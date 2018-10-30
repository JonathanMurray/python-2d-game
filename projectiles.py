def apply_projectile_enemy_collision_effect(enemy):
    enemy.lose_health(1)


def apply_projectile_player_collision_effect(player_state):
    player_state.lose_health(10)
