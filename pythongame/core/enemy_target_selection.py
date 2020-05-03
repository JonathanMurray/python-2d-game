from typing import Optional

from pythongame.core.game_data import NpcCategory
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.math import get_manhattan_distance
from pythongame.core.world_entity import WorldEntity


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
    # Enemies should prioritize attacking a summon over attacking the player
    player_summons = [npc for npc in game_state.game_world.non_player_characters
                      if npc.npc_category == NpcCategory.PLAYER_SUMMON]
    if player_summons:
        player_summon = player_summons[0]
        agent_position = agent_entity.get_position()
        distance_to_npc_target = get_manhattan_distance(player_summon.world_entity.get_position(),
                                                        agent_position)
        distance_to_player = get_manhattan_distance(game_state.game_world.player_entity.get_position(), agent_position)
        if distance_to_npc_target < distance_to_player:
            return EnemyTarget.npc(player_summon.world_entity, player_summon)
    return EnemyTarget.player(game_state.game_world.player_entity)
