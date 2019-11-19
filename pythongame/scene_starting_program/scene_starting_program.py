from typing import Optional

from pythongame.core.common import HeroId, Millis, AbstractScene, SceneTransition, SceneId
from pythongame.player_file import load_player_state_from_json_file
from pythongame.scene_creating_world.scene_creating_world import InitFlags


class CommandlineFlags:
    def __init__(self, map_file_name: Optional[str], picked_hero: Optional[HeroId],
                 load_from_file: Optional[str],
                 hero_start_level: int, start_money: int):
        self.map_file_name = map_file_name
        self.chosen_hero_id = picked_hero
        self.load_from_file = load_from_file
        self.hero_start_level = hero_start_level
        self.start_money = start_money

    def __repr__(self):
        return "(" + str(self.map_file_name) + ", " + str(self.chosen_hero_id) + ", " + \
               str(self.load_from_file) + ", " + str(self.hero_start_level) + ", " + str(self.start_money) + ")"


class StartingProgramScene(AbstractScene):
    def __init__(self):

        # Set on initialization
        self.cmd_flags: CommandlineFlags = None

    def initialize(self, cmd_flags: CommandlineFlags):
        self.cmd_flags = cmd_flags  # map hero money level

    def run_one_frame(self, _time_passed: Millis, _fps_string: str) -> Optional[SceneTransition]:

        map_file_name = self.cmd_flags.map_file_name or "map1.json"
        map_file_path = "resources/maps/" + map_file_name

        start_immediately_and_skip_hero_selection = (
                self.cmd_flags.chosen_hero_id is not None
                or self.cmd_flags.hero_start_level is not None
                or self.cmd_flags.start_money is not None
                or self.cmd_flags.load_from_file is not None)

        if start_immediately_and_skip_hero_selection:
            saved_player_state = load_player_state_from_json_file(
                "savefiles/" + self.cmd_flags.load_from_file) if self.cmd_flags.load_from_file else None
            if saved_player_state:
                picked_hero = HeroId[saved_player_state.hero_id]
            elif self.cmd_flags.chosen_hero_id:
                picked_hero = HeroId[self.cmd_flags.chosen_hero_id]
            else:
                picked_hero = HeroId.MAGE
            hero_start_level = int(self.cmd_flags.hero_start_level) if self.cmd_flags.hero_start_level else 1
            start_money = int(self.cmd_flags.start_money) if self.cmd_flags.start_money else 0

            flags = InitFlags(
                map_file_path,
                picked_hero,
                saved_player_state,
                hero_start_level,
                start_money)
            return SceneTransition(SceneId.CREATING_GAME_WORLD, flags)

        else:
            flags = InitFlags(
                map_file_path=map_file_path,
                picked_hero=None,
                saved_player_state=None,
                hero_start_level=1,
                start_money=0)
            return SceneTransition(SceneId.PICKING_HERO, flags)
