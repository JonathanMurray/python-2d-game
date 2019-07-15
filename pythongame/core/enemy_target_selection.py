from typing import Optional

from pythongame.core.game_state import WorldEntity, GameState, NonPlayerCharacter
from pythongame.core.math import get_manhattan_distance


# Represents a hostile target for an enemy.
# 2 possibilities:
# - another NPC (a summon owned by the player for instance)
# - the player
class EnemyTarget:
    def __init__(self, entity: WorldEntity, non_enemy_npc: Optional[NonPlayerCharacter]):
        self.entity = entity
        self.non_enemy_npc = non_enemy_npc

    @staticmethod
    def player(player_entity: WorldEntity):
        return EnemyTarget(player_entity, None)

    @staticmethod
    def npc(entity: WorldEntity, non_enemy_npc: NonPlayerCharacter):
        return EnemyTarget(entity, non_enemy_npc)


def get_target(agent_entity: WorldEntity, game_state: GameState) -> EnemyTarget:
    # neutral NPCs (like quest givers) should not be attacked by enemies!
    potential_npc_targets = [npc for npc in game_state.non_enemy_npcs if not npc.is_neutral]
    if potential_npc_targets:
        arbitrary_npc_target = potential_npc_targets[0]
        agent_position = agent_entity.get_position()
        distance_to_npc_target = get_manhattan_distance(arbitrary_npc_target.world_entity.get_position(),
                                                        agent_position)
        distance_to_player = get_manhattan_distance(game_state.player_entity.get_position(), agent_position)
        if distance_to_npc_target < distance_to_player:
            return EnemyTarget.npc(arbitrary_npc_target.world_entity, arbitrary_npc_target)
    return EnemyTarget.player(game_state.player_entity)
