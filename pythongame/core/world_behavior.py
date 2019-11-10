from typing import Optional

from pythongame.core.common import Millis, SceneTransition
from pythongame.scenes_game.game_engine import EngineEvent


class AbstractWorldBehavior:

    def on_startup(self):
        pass

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        pass

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        pass
