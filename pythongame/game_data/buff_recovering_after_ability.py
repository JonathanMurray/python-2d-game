from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect
from pythongame.core.common import BuffType
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE = BuffType.RECOVERING_AFTER_ABILITY


class RecoveringAfterAbility(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.game_world.player_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()

    def get_buff_type(self):
        return BUFF_TYPE


def register_recovering_after_ability_buff():
    register_buff_effect(BUFF_TYPE, RecoveringAfterAbility)
