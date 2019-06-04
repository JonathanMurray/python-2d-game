from pythongame.core.ability_effects import apply_ability_effect
from pythongame.core.common import AbilityType, Millis, SoundId
from pythongame.core.consumable_effects import try_consume_consumable, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed
from pythongame.core.game_data import ABILITIES
from pythongame.core.game_state import GameState
from pythongame.core.sound_player import play_sound
from pythongame.core.view_state import ViewState

# global cooldown.
# TODO: Should this be a thing? If so, it should be shown more clearly in the UI.
ABILITY_COOLDOWN = 200


class PlayerControls:
    def __init__(self):
        self.ticks_since_ability_used = ABILITY_COOLDOWN

    def try_use_ability(self, ability_type: AbilityType, game_state: GameState, view_state: ViewState):
        if game_state.player_state.is_stunned:
            return
        view_state.notify_ability_was_clicked(ability_type)
        player_state = game_state.player_state
        if self.ticks_since_ability_used < ABILITY_COOLDOWN:
            return

        self.ticks_since_ability_used = 0
        ability_data = ABILITIES[ability_type]
        mana_cost = ability_data.mana_cost

        if player_state.mana < mana_cost:
            play_sound(SoundId.WARNING)
            view_state.set_message("Not enough mana!")
            return

        if player_state.ability_cooldowns_remaining[ability_type] > 0:
            return

        did_execute = apply_ability_effect(game_state, ability_type)
        if did_execute:
            if ability_data.sound_id:
                play_sound(ability_data.sound_id)
            else:
                print("WARN: No sound defined for ability: " + str(ability_type))
            player_state.lose_mana(mana_cost)
            player_state.ability_cooldowns_remaining[ability_type] = ability_data.cooldown
            return
        else:
            view_state.set_message("Failed to execute ability!")

    def notify_time_passed(self, time_passed: Millis):
        self.ticks_since_ability_used += time_passed

    def try_use_consumable(self, slot_number: int, game_state: GameState, view_state: ViewState):

        if not game_state.player_state.is_stunned:
            view_state.notify_consumable_was_clicked(slot_number)
            consumable_type_in_this_slot = game_state.player_state.consumable_slots[slot_number]
            if consumable_type_in_this_slot:
                result = try_consume_consumable(consumable_type_in_this_slot, game_state)
                if isinstance(result, ConsumableWasConsumed):
                    game_state.player_state.consumable_slots[slot_number] = None
                    if result.message:
                        view_state.set_message(result.message)
                    play_sound(SoundId.POTION)
                elif isinstance(result, ConsumableFailedToBeConsumed):
                    view_state.set_message(result.reason)
            else:
                view_state.set_message("Nothing to use!")

    # TODO Move more player controls into this package?
