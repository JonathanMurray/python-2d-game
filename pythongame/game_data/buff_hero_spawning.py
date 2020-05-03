from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Millis, BuffType, SoundId
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.sound_player import play_sound
from pythongame.core.visual_effects import create_teleport_effects
from pythongame.core.world_entity import WorldEntity

BUFF_TYPE = BuffType.BEING_SPAWNED
DELAY = Millis(1000)


class BeingSpawned(AbstractBuffEffect):
    def __init__(self):
        self.time_since_start = 0
        self.has_spawn_happened = False

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.game_world.player_entity.set_not_moving()
        game_state.game_world.player_entity.visible = False

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self.time_since_start += time_passed
        if not self.has_spawn_happened and self.time_since_start > DELAY / 2:
            self.has_spawn_happened = True
            game_state.game_world.visual_effects += create_teleport_effects(buffed_entity.get_center_position())
            play_sound(SoundId.ABILITY_TELEPORT)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        game_state.game_world.player_entity.visible = True

    def get_buff_type(self):
        return BUFF_TYPE


def register_spawn_buff():
    register_buff_effect(BUFF_TYPE, BeingSpawned)
