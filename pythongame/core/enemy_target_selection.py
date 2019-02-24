from typing import Optional

from pythongame.core.common import get_manhattan_distance
from pythongame.core.game_state import WorldEntity, GameState, NonPlayerCharacter


# Represents a hostile target for an enemy.
# 2 possibilities:
# - another NPC (a summon owned by the player for instance)
# - the player
class EnemyTarget:
    def __init__(self, entity: WorldEntity, non_enemy_npc: Optional[NonPlayerCharacter]):
        self.entity = entity
        self.non_enemy_npc = non_enemy_npc


def get_target(agent_entity: WorldEntity, game_state: GameState) -> EnemyTarget:
    if game_state.non_enemy_npcs:
        npc_target = game_state.non_enemy_npcs[0]
        agent_position = agent_entity.get_position()
        distance_to_npc = get_manhattan_distance(npc_target.world_entity.get_position(), agent_position)
        distance_to_player = get_manhattan_distance(game_state.player_entity.get_position(), agent_position)
        if distance_to_npc < distance_to_player:
            return EnemyTarget(npc_target.world_entity, npc_target)
    return EnemyTarget(game_state.player_entity, None)
