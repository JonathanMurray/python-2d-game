from typing import Optional

from pythongame.core.common import Millis, SceneId


class AbstractWorldBehavior:

    def on_startup(self):
        pass

    def control(self, time_passed: Millis) -> Optional[SceneId]:
        pass

    def handle_player_died(self) -> Optional[SceneId]:
        pass
