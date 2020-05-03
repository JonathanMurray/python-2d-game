from typing import Optional, Callable, Tuple

from pythongame.core.common import Millis, AbstractScene, AbstractWorldBehavior
from pythongame.core.game_state import GameState
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import GameUiView


class AbstractSceneFactory:

    # flags are InitFlags
    def main_menu_scene(self, flags) -> AbstractScene:
        raise Exception("Not implemented")

    # flags are InitFlags
    def creating_world_scene(self, flags) -> AbstractScene:
        raise Exception("Not implemented")

    # flags are InitFlags
    def picking_hero_scene(self, init_flags) -> AbstractScene:
        raise Exception("Not implemented")

    def playing_scene(
            self, game_state: GameState, game_engine: GameEngine, world_behavior: AbstractWorldBehavior,
            ui_view: GameUiView, new_hero_was_created: bool, character_file: Optional[str],
            total_time_played_on_character: Millis) -> AbstractScene:
        raise Exception("Not implemented")

    def challenge_complete_scene(self, total_time_played: Millis) -> AbstractScene:
        raise Exception("Not implemented")

    def victory_screen_scene(self) -> AbstractScene:
        raise Exception("Not implemented")

    def switching_game_world(
            self,
            game_engine: GameEngine,
            character_file: str,
            total_time_played_on_character: Millis,
            create_new_game_engine_and_behavior: Callable[[GameEngine], Tuple[GameEngine, AbstractWorldBehavior]]) \
            -> AbstractScene:
        raise Exception("Not implemented")
