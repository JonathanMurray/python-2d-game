#!/usr/bin/env python3
from pythongame.core.common import NpcType
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, NpcCategory
from pythongame.register_game_data import register_all_game_data


def print_enemies():
    enemy_types_and_data = [(npc_type, NON_PLAYER_CHARACTERS[npc_type]) for npc_type in NpcType if
                            NON_PLAYER_CHARACTERS[npc_type].npc_category == NpcCategory.ENEMY]
    enemy_types_and_data.sort(key=lambda x: x[1].exp_reward)
    for enemy_type, enemy_data in enemy_types_and_data:
        print("{:<25}".format(enemy_type.name) + str(enemy_data.max_health) + " HP, "
              + str(enemy_data.exp_reward) + " xp")


register_all_game_data()
print_enemies()
