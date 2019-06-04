from enum import Enum

from pythongame.core.ability_effects import apply_ability_effect
from pythongame.core.common import AbilityType, Millis
from pythongame.core.game_data import ABILITIES
from pythongame.core.game_state import GameState
from pythongame.core.sound_engine import SoundEngine

# global cooldown.
# TODO: Should this be a thing? If so, it should be shown more clearly in the UI.
ABILITY_COOLDOWN = 200


class TryUseAbilityResult(Enum):
    SUCCESS = 1
    NOT_ENOUGH_MANA = 2
    COOLDOWN_NOT_READY = 3
    FAILED_TO_EXECUTE = 4


class PlayerControls:
    def __init__(self):
        self.ticks_since_ability_used = ABILITY_COOLDOWN

    def try_use_ability(self, ability_type: AbilityType, game_state: GameState, sound_engine: SoundEngine):
        player_state = game_state.player_state
        if self.ticks_since_ability_used < ABILITY_COOLDOWN:
            return TryUseAbilityResult.COOLDOWN_NOT_READY

        self.ticks_since_ability_used = 0
        ability_data = ABILITIES[ability_type]
        mana_cost = ability_data.mana_cost

        if player_state.mana < mana_cost:
            return TryUseAbilityResult.NOT_ENOUGH_MANA

        if player_state.ability_cooldowns_remaining[ability_type] > 0:
            return TryUseAbilityResult.COOLDOWN_NOT_READY

        did_execute = apply_ability_effect(game_state, ability_type)
        if did_execute:
            if ability_data.sound_id:
                sound_engine.play_sound(ability_data.sound_id)
            else:
                print("WARN: No sound defined for ability: " + str(ability_type))
            player_state.lose_mana(mana_cost)
            player_state.ability_cooldowns_remaining[ability_type] = ability_data.cooldown
            return TryUseAbilityResult.SUCCESS
        else:
            return TryUseAbilityResult.FAILED_TO_EXECUTE

    def notify_time_passed(self, time_passed: Millis):
        self.ticks_since_ability_used += time_passed

    # TODO Move more player controls into this package?
