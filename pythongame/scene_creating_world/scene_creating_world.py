from typing import Optional
from typing import Tuple

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import ItemType, \
    ConsumableType, Sprite
from pythongame.core.common import SceneId, Millis, HeroId, BuffType, get_random_hint, \
    SoundId, HeroUpgrade, AbstractScene, SceneTransition
from pythongame.core.consumable_inventory import ConsumableInventory
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_state import GameState
from pythongame.core.sound_player import play_sound
from pythongame.core.world_behavior import AbstractWorldBehavior
from pythongame.map_file import create_game_state_from_json_file
from pythongame.player_file import SavedPlayerState
from pythongame.scenes_game.game_engine import GameEngine
from pythongame.scenes_game.game_ui_state import GameUiState


class InitFlags:
    def __init__(self, map_file_path: Optional[str], picked_hero: Optional[HeroId],
                 saved_player_state: Optional[SavedPlayerState],
                 hero_start_level: int, start_money: int):
        self.map_file_path = map_file_path
        self.picked_hero = picked_hero
        self.saved_player_state = saved_player_state
        self.hero_start_level = hero_start_level
        self.start_money = start_money

    def __repr__(self):
        return "(" + self.map_file_path + ", " + str(self.picked_hero) + ", " + \
               str(self.saved_player_state) + ", " + str(self.hero_start_level) + ", " + str(self.start_money) + ")"


class StandardWorldBehavior(AbstractWorldBehavior):

    def __init__(self, game_state: GameState, ui_state: GameUiState):
        self.game_state = game_state
        self.ui_state = ui_state

    def on_startup(self):
        self.ui_state.set_message("Hint: " + get_random_hint())

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        if self.game_state.player_state.has_upgrade(HeroUpgrade.HAS_WON_GAME):
            return SceneTransition(SceneId.VICTORY_SCREEN, None)

    def handle_player_died(self) -> Optional[SceneTransition]:
        self.game_state.player_entity.set_position(self.game_state.player_spawn_position)
        self.game_state.player_state.health_resource.set_to_partial_of_max(0.5)
        self.game_state.player_state.lose_exp_from_death()
        self.game_state.player_state.force_cancel_all_buffs()
        self.ui_state.set_message("Lost exp from dying")
        play_sound(SoundId.EVENT_PLAYER_DIED)
        self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        return None


class ChallengeWorldBehavior(AbstractWorldBehavior):

    def __init__(self, game_state: GameState, ui_state: GameUiState, game_engine: GameEngine):
        self.game_state = game_state
        self.ui_state = ui_state
        self.game_engine = game_engine
        self.total_time_played = 0

    def on_startup(self):
        self.ui_state.set_message("Challenge starting...")
        self.game_state.player_state.money += 100
        self.game_engine.gain_levels(6)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        self.total_time_played += time_passed
        if self.game_state.player_state.has_upgrade(HeroUpgrade.HAS_WON_GAME):
            return SceneTransition(SceneId.CHALLENGE_COMPLETE_SCREEN, self.total_time_played)

    def handle_player_died(self) -> Optional[SceneTransition]:
        print("TODO: Go to some other screen")
        return SceneTransition(SceneId.PICKING_HERO, None)


class CreatingWorldScene(AbstractScene):
    def __init__(self, camera_size: Tuple[int, int]):

        self.camera_size = camera_size

        self.flags: InitFlags = None

    def initialize(self, flags: InitFlags):
        self.flags = flags  # map hero money level

    def run_one_frame(self, _time_passed: Millis, _fps_string: str) -> Optional[SceneTransition]:

        saved_player_state = self.flags.saved_player_state
        hero_start_level = self.flags.hero_start_level
        start_money = self.flags.start_money

        game_state = create_game_state_from_json_file(self.camera_size, self.flags.map_file_path,
                                                      self.flags.picked_hero)
        ui_state = GameUiState()
        game_engine = GameEngine(game_state, ui_state)
        if self.flags.map_file_path == 'resources/maps/challenge.json':
            world_behavior = ChallengeWorldBehavior(game_state, ui_state, game_engine)
        else:
            world_behavior = StandardWorldBehavior(game_state, ui_state)

        if saved_player_state:
            game_state.player_state.gain_exp_worth_n_levels(saved_player_state.level - 1)
            game_state.player_state.gain_exp(saved_player_state.exp)
            game_engine.set_item_inventory([ItemType[item] if item else None for item in saved_player_state.items])
            game_state.player_state.consumable_inventory = ConsumableInventory(
                {int(slot_number): [ConsumableType[c] for c in consumables] for (slot_number, consumables)
                 in saved_player_state.consumables_in_slots.items()}
            )
            game_state.player_state.money += saved_player_state.money
            for portal in game_state.portals:
                if portal.portal_id.name in saved_player_state.enabled_portals:
                    sprite = saved_player_state.enabled_portals[portal.portal_id.name]
                    portal.activate(Sprite[sprite])
        else:
            if hero_start_level > 1:
                game_state.player_state.gain_exp_worth_n_levels(hero_start_level - 1)
            if start_money > 0:
                game_state.player_state.money += start_money

        allocate_input_keys_for_abilities(game_state.player_state.abilities)

        game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))

        return SceneTransition(SceneId.PLAYING, (game_state, game_engine, world_behavior, ui_state))
