from pythongame.core.ability_effects import apply_ability_effect, AbilityFailedToExecute, \
    AbilityWasUsedSuccessfully
from pythongame.core.common import AbilityType, SoundId, Millis
from pythongame.core.consumable_effects import try_consume_consumable, ConsumableWasConsumed, \
    ConsumableFailedToBeConsumed
from pythongame.core.game_data import ABILITIES
from pythongame.core.game_state import GameState, PlayerUsedAbilityEvent
from pythongame.core.sound_player import play_sound
from pythongame.core.view.view_state import ViewState


class PlayerControls:

    @staticmethod
    def try_use_ability(ability_type: AbilityType, game_state: GameState, view_state: ViewState):
        if game_state.player_state.stun_status.is_stunned():
            return
        view_state.notify_ability_was_clicked(ability_type)
        player_state = game_state.player_state

        ability_data = ABILITIES[ability_type]
        mana_cost = ability_data.mana_cost

        if player_state.ability_cooldowns_remaining[ability_type] > 0:
            return

        if player_state.mana_resource.value < mana_cost:
            play_sound(SoundId.INVALID_ACTION)
            view_state.set_message("Not enough mana!")
            player_state.ability_cooldowns_remaining[ability_type] = Millis(500)
            return

        ability_result = apply_ability_effect(game_state, ability_type)
        if isinstance(ability_result, AbilityFailedToExecute):
            message = "Can't do that!" + (" (" + ability_result.reason + ")" if ability_result.reason else "")
            view_state.set_message(message)
            play_sound(SoundId.INVALID_ACTION)
            player_state.ability_cooldowns_remaining[ability_type] = Millis(500)
        elif isinstance(ability_result, AbilityWasUsedSuccessfully):
            if ability_data.sound_id:
                play_sound(ability_data.sound_id)
            else:
                print("WARN: No sound defined for ability: " + str(ability_type))
            if ability_result.should_regain_mana_and_cd:
                # The cooldown is reset to almost 0. We set it to 500 to avoid it being used twice because of ability
                # key being held down by user.
                player_state.ability_cooldowns_remaining[ability_type] += Millis(500)
            else:
                player_state.mana_resource.lose(mana_cost)
                player_state.ability_cooldowns_remaining[ability_type] += ability_data.cooldown
            game_state.player_state.notify_about_event(PlayerUsedAbilityEvent(ability_type), game_state)
        else:
            raise Exception("Unhandled ability effect result: " + str(ability_result))

    @staticmethod
    def try_use_consumable(slot_number: int, game_state: GameState, view_state: ViewState):

        view_state.notify_consumable_was_clicked(slot_number)
        consumable_type_in_this_slot = \
            game_state.player_state.consumable_inventory.get_consumable_at_slot(slot_number)
        if consumable_type_in_this_slot:
            result = try_consume_consumable(consumable_type_in_this_slot, game_state)
            if isinstance(result, ConsumableWasConsumed):
                game_state.player_state.consumable_inventory.remove_consumable_from_slot(slot_number)
                if result.message:
                    view_state.set_message(result.message)
                play_sound(SoundId.POTION)
            elif isinstance(result, ConsumableFailedToBeConsumed):
                play_sound(SoundId.INVALID_ACTION)
                view_state.set_message(result.reason)
        else:
            play_sound(SoundId.INVALID_ACTION)
            view_state.set_message("Nothing to use!")

    # TODO Move more player controls into this package?
