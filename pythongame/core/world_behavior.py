from typing import Optional

from pythongame.core.common import Millis, SceneTransition


class AbstractWorldBehavior:

    def on_startup(self):
        pass

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        pass

    def handle_player_died(self) -> Optional[SceneTransition]:
        pass
