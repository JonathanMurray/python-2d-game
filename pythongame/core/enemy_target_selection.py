from typing import Optional

from pythongame.core.game_state import WorldEntity, GameState, NonPlayerCharacter


# Represents a hostile target for an enemy.
# 2 possibilities:
# - another NPC (a summon owned by the player for instance)
# - the player
class EnemyTarget:
    def __init__(self, entity: WorldEntity, non_enemy_npc: Optional[NonPlayerCharacter]):
        self.entity = entity
        self.non_enemy_npc = non_enemy_npc


def get_target(game_state: GameState) -> EnemyTarget:
    if game_state.non_enemy_npcs:
        npc_target = game_state.non_enemy_npcs[0]
        return EnemyTarget(npc_target.world_entity, npc_target)
    else:
        return EnemyTarget(game_state.player_entity, None)
