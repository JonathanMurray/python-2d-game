from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Millis, PeriodicTimer, BuffType
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity

SPRINT_SPEED_BONUS = 0.7
BUFF_SPRINT = BuffType.ENEMY_GOBLIN_SPEARMAN_SPRINT


class BuffEffect(AbstractBuffEffect):

    def __init__(self):
        self.graphics_timer = PeriodicTimer(Millis(500))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(SPRINT_SPEED_BONUS)
        self.create_sprint_visual_effect(buffed_entity, game_state)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.graphics_timer.update_and_check_if_ready(time_passed):
            self.create_sprint_visual_effect(buffed_entity, game_state)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(-SPRINT_SPEED_BONUS)

    def get_buff_type(self):
        return BUFF_SPRINT

    @staticmethod
    def create_sprint_visual_effect(buffed_entity: WorldEntity, game_state: GameState):
        game_state.game_world.visual_effects.append(
            VisualCircle((150, 50, 0), buffed_entity.get_center_position(), 20, 22, Millis(250), 2, buffed_entity))


def register_goblin_sprint_buff():
    register_buff_effect(BUFF_SPRINT, BuffEffect)
