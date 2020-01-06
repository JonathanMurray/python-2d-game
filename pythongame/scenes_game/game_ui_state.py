from pythongame.core.common import Millis

MESSAGE_DURATION = 3500


# This class maintains the UI state that's related to the game clock. For instance, when the player clicks a button in
# the UI, it should be highlighted but only for a while. Keeping that logic here lets main.py be free from UI details
# and it lets view.py be stateless.
class GameUiState:
    def __init__(self):
        self._ticks_since_message_updated = 0

        self.message = ""
        self._enqueued_messages = []

    def set_message(self, message: str):
        self.message = message
        self._ticks_since_message_updated = 0

    def enqueue_message(self, message: str):
        self._enqueued_messages.append(message)

    def clear_messages(self):
        self.message = None
        self._enqueued_messages.clear()

    def notify_time_passed(self, time_passed: Millis):
        self._ticks_since_message_updated += time_passed
        if self.message != "" and self._ticks_since_message_updated > MESSAGE_DURATION:
            if self._enqueued_messages:
                new_message = self._enqueued_messages.pop(0)
                self.set_message(new_message)
            else:
                self.message = ""
