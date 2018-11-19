from typing import Tuple, Optional

from pythongame.core.common import AbilityType, Millis

MINIMAP_UPDATE_INTERVAL = 1000
MESSAGE_DURATION = 2500
HIGHLIGHT_POTION_ACTION_DURATION = 120
HIGHLIGHT_ABILITY_ACTION_DURATION = 120


# This class maintains the UI state that's related to the game clock. For instance, when the player clicks a button in
# the UI, it should be highlighted but only for a while. Keeping that logic here lets main.py be free from UI details
# and it lets view.py be stateless.
class ViewState:
    def __init__(self, game_world_size: Tuple[int, int]):
        self._game_world_size = game_world_size
        self._player_entity_center_position = (0, 0)
        self._ticks_since_minimap_updated = MINIMAP_UPDATE_INTERVAL
        self._ticks_since_message_updated = 0
        self._ticks_since_last_potion_action = 0
        self._ticks_since_last_ability_action = 0

        self.player_minimap_relative_position: Tuple[float, float] = (0, 0)
        self.message = ""
        self.highlighted_potion_action: Optional[int] = None
        self.highlighted_ability_action: Optional[AbilityType] = None

    def notify_ability_was_clicked(self, ability_type: AbilityType):
        self.highlighted_ability_action = ability_type
        self._ticks_since_last_ability_action = 0

    def notify_potion_was_clicked(self, slot_number: int):
        self.highlighted_potion_action = slot_number
        self._ticks_since_last_potion_action = 0

    def notify_player_entity_center_position(self, player_entity_center_position: Tuple[int, int]):
        self._player_entity_center_position = player_entity_center_position

    def set_message(self, message):
        self.message = message
        self._ticks_since_message_updated = 0

    def notify_time_passed(self, time_passed: Millis):
        self._ticks_since_minimap_updated += time_passed
        if self._ticks_since_minimap_updated > MINIMAP_UPDATE_INTERVAL:
            self._ticks_since_minimap_updated = 0
            self.player_minimap_relative_position = (self._player_entity_center_position[0] / self._game_world_size[0],
                                                     self._player_entity_center_position[1] / self._game_world_size[1])

        self._ticks_since_message_updated += time_passed
        if self._ticks_since_message_updated > MESSAGE_DURATION:
            self.message = ""

        self._ticks_since_last_potion_action += time_passed
        if self._ticks_since_last_potion_action > HIGHLIGHT_POTION_ACTION_DURATION:
            self.highlighted_potion_action = None

        self._ticks_since_last_ability_action += time_passed
        if self._ticks_since_last_ability_action > HIGHLIGHT_ABILITY_ACTION_DURATION:
            self.highlighted_ability_action = None
