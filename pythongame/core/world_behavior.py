from typing import Optional, Tuple

from pythongame.core.buff_effects import get_buff_effect
from pythongame.core.common import ConsumableType, ItemId, AbstractWorldBehavior, EngineEvent, PeriodicTimer
from pythongame.core.common import ItemType
from pythongame.core.common import Millis, BuffType, get_random_hint, \
    SoundId, SceneTransition
from pythongame.core.game_data import HEROES
from pythongame.core.game_state import GameState
from pythongame.core.item_data import randomized_item_id
from pythongame.core.sound_player import play_sound
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import InfoMessage, GameUiView


class StoryBehavior(AbstractWorldBehavior):

    def __init__(self, scene_factory: AbstractSceneFactory, game_engine: GameEngine, game_state: GameState,
                 ui_view: GameUiView):
        self.scene_factory = scene_factory
        self.game_engine = game_engine
        self.game_state = game_state
        self.ui_view = ui_view

    def on_startup(self, new_hero_was_created: bool):
        self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        self.ui_view.info_message.set_message("Hint: " + get_random_hint())
        self.ui_view.update_game_mode_string("")
        if new_hero_was_created:
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.HEALTH_LESSER)
            self.game_state.player_state.consumable_inventory.add_consumable(ConsumableType.MANA_LESSER)
            for item_id in HEROES[self.game_state.player_state.hero_id].initial_player_state.starting_items:
                self.add_starting_item(item_id)

    def add_starting_item(self, item_id: ItemId):
        self.game_engine.try_add_item_to_inventory(item_id)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        pass
        # uncomment to conditionally go to victory screen
        # if self.game_state.player_state.has_completed_quest(QuestId.MAIN_RETRIEVE_KEY):
        #    return SceneTransition(self.victory_screen_scene())

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        if event == EngineEvent.PLAYER_DIED:
            self.game_state.game_world.player_entity.set_position(self.game_state.player_spawn_position)
            self.game_state.player_state.health_resource.set_to_partial_of_max(0.5)
            self.game_state.player_state.lose_exp_from_death()
            self.game_state.player_state.force_cancel_all_buffs()
            self.ui_view.info_message.set_message("Lost exp from dying")
            play_sound(SoundId.EVENT_PLAYER_DIED)
            self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        return None


class DungeonBehavior(AbstractWorldBehavior):

    def __init__(self,
                 scene_factory: AbstractSceneFactory,
                 game_state_before_entering_dungeon: GameState,
                 game_engine: GameEngine,
                 ui_view: GameUiView,
                 character_file: str,
                 total_time_played_on_character: Millis):
        self.scene_factory = scene_factory
        self.game_state_before_entering_dungeon = game_state_before_entering_dungeon
        self.game_engine = game_engine
        self.game_state = game_engine.game_state
        self.ui_view = ui_view
        self.character_file = character_file
        self.total_time_played_on_character = total_time_played_on_character
        self.countdown_until_hero_will_be_warped_out_of_dungeon: int = None
        self.warp_countdown_timer: PeriodicTimer = None

    def on_startup(self, new_hero_was_created: bool):
        self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        self.ui_view.info_message.set_message("Fight through all enemies to get out!")
        self.ui_view.update_game_mode_string("Dungeon %i" % self.game_state.player_state.dungeon_difficulty_level)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        if self.warp_countdown_timer is not None:
            if self.warp_countdown_timer.update_and_check_if_ready(time_passed):
                if self.countdown_until_hero_will_be_warped_out_of_dungeon > 0:
                    self.ui_view.info_message.set_message(
                        "You will be warped out in %s" % self.countdown_until_hero_will_be_warped_out_of_dungeon)
                    self.countdown_until_hero_will_be_warped_out_of_dungeon -= 1
                else:
                    self.game_state.player_state.dungeon_difficulty_level += 1
                    return self._transition_out_of_dungeon()

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        if event == EngineEvent.PLAYER_DIED:

            # If player has any movement buffs/debuffs that affect the hero entity, and the buff was retained when we
            # switch back to the old game state, then we'd incorrectly modify the hero entity when it expires
            self.game_state.player_state.force_cancel_all_buffs()

            # Player will "die again" outside of the dungeon which will trigger exp loss and respawning at base
            # TODO spawn animation doesn't work? Maybe we should just set HP to 1 and let hero spawn at entrance
            return self._transition_out_of_dungeon()
        elif event == EngineEvent.ENEMY_DIED:
            num_enemies = len([npc for npc in self.game_state.game_world.non_player_characters if npc.is_enemy])
            if num_enemies == 0:
                self.ui_view.info_message.set_message("Dungeon cleared!")
                self.warp_countdown_timer = PeriodicTimer(Millis(1000))
                self.countdown_until_hero_will_be_warped_out_of_dungeon = 5
            else:
                self.ui_view.info_message.set_message(str(num_enemies) + " enemies remaining in dungeon")
        return None

    def _transition_out_of_dungeon(self):
        scene = self.scene_factory.switching_game_world(
            self.game_engine,
            self.character_file,
            self.total_time_played_on_character,
            self._recreate_main_world_engine_and_behavior
        )
        return SceneTransition(scene)

    def _recreate_main_world_engine_and_behavior(self, _: GameEngine) -> Tuple[GameEngine, AbstractWorldBehavior]:
        game_state = self.game_state_before_entering_dungeon
        engine = GameEngine(game_state, self.ui_view.info_message)
        behavior = StoryBehavior(self.scene_factory, engine, game_state, self.ui_view)
        return engine, behavior


class ChallengeBehavior(AbstractWorldBehavior):
    def __init__(self,
                 scene_factory: AbstractSceneFactory,
                 game_state: GameState,
                 info_message: InfoMessage,
                 game_engine: GameEngine,
                 init_flags):
        self.scene_factory = scene_factory
        self.game_state = game_state
        self.info_message = info_message
        self.game_engine = game_engine
        self.total_time_played: Millis = 0
        self.init_flags = init_flags

    def on_startup(self, new_hero_was_created: bool):
        self.game_state.player_state.gain_buff_effect(get_buff_effect(BuffType.BEING_SPAWNED), Millis(1000))
        self.info_message.set_message("Challenge starting...")
        if new_hero_was_created:
            self.game_state.player_state.modify_money(100)
            self.game_engine.gain_levels(4)

            consumables = [ConsumableType.HEALTH,
                           ConsumableType.HEALTH,
                           ConsumableType.MANA,
                           ConsumableType.MANA,
                           ConsumableType.SPEED,
                           ConsumableType.POWER]
            for consumable_type in consumables:
                self.game_state.player_state.consumable_inventory.add_consumable(consumable_type)
            items = [randomized_item_id(ItemType.LEATHER_COWL), randomized_item_id(ItemType.LEATHER_ARMOR),
                     randomized_item_id(ItemType.PRACTICE_SWORD), randomized_item_id(ItemType.WOODEN_SHIELD)]
            for item_type in items:
                self._equip_item_on_startup(item_type)

    def _equip_item_on_startup(self, item_id):
        self.game_engine.try_add_item_to_inventory(item_id)

    def control(self, time_passed: Millis) -> Optional[SceneTransition]:
        self.total_time_played += time_passed
        return None

    def handle_event(self, event: EngineEvent) -> Optional[SceneTransition]:
        if event == EngineEvent.PLAYER_DIED:
            return SceneTransition(self.scene_factory.picking_hero_scene(self.init_flags))
        elif event == EngineEvent.ENEMY_DIED:
            num_enemies = len([npc for npc in self.game_state.game_world.non_player_characters if npc.is_enemy])
            if num_enemies == 0:
                return SceneTransition(self.scene_factory.challenge_complete_scene(self.total_time_played))
            self.info_message.set_message(str(num_enemies) + " enemies remaining")
        return None
