from typing import Optional

from pythongame.core.common import Millis, AbstractScene, SceneTransition
from pythongame.core.entity_creation import create_hero_world_entity
from pythongame.core.game_state import GameState
from pythongame.core.global_path_finder import init_global_path_finder
from pythongame.core.world_behavior import DungeonBehavior
from pythongame.dungeon_generator import DungeonGenerator, GeneratedDungeon
from pythongame.scenes.scene_factory import AbstractSceneFactory
from pythongame.scenes.scenes_game.game_engine import GameEngine
from pythongame.scenes.scenes_game.game_ui_view import GameUiView
from pythongame.world_init_util import register_game_engine_observers, register_game_state_observers


class EnteringDungeonScene(AbstractScene):
    def __init__(
            self,
            scene_factory: AbstractSceneFactory,
            game_engine: GameEngine,
            ui_view: GameUiView,
            character_file: str,
            total_time_played_on_character: Millis):
        self.scene_factory = scene_factory
        self.previous_game_engine = game_engine
        self.ui_view = ui_view
        self.character_file = character_file
        self.total_time_played_on_character = total_time_played_on_character

    def run_one_frame(self, _time_passed: Millis) -> Optional[SceneTransition]:
        # NPC's share a "global path finder" that needs to be initialized before we start creating NPCs.
        # TODO This is very messy
        path_finder = init_global_path_finder()

        dungeon_generator = DungeonGenerator()
        dungeon_grid, dungeon_rooms = dungeon_generator.generate_random_grid()
        dungeon: GeneratedDungeon = dungeon_generator.generate_random_dungeon_from_grid(dungeon_grid, dungeon_rooms)

        # We do this to temporarily deactivate all item effects, to later re-activate them with the new game state
        # (mainly because of how movement speed item effects modify the hero entity in the game state)
        item_inventory_slots = self.previous_game_engine.clear_item_inventory()

        previous_game_state = self.previous_game_engine.game_state
        hero_id = previous_game_state.player_state.hero_id

        game_state = GameState(player_entity=create_hero_world_entity(hero_id, dungeon.player_position),
                               consumables_on_ground=[],
                               items_on_ground=[],
                               money_piles_on_ground=[],
                               non_player_characters=dungeon.npcs,
                               walls=dungeon.walls,
                               camera_size=previous_game_state.camera_size,
                               entire_world_area=dungeon.world_area,
                               player_state=previous_game_state.player_state,
                               decoration_entities=dungeon.decorations,
                               portals=[],
                               chests=[],
                               shrines=[],
                               dungeon_entrances=[])

        path_finder.set_grid(game_state.pathfinder_wall_grid)

        # Must center camera before notifying player position as it affects which walls are shown on the minimap
        game_state.center_camera_on_player()
        self.ui_view.on_world_area_updated(game_state.entire_world_area)
        self.ui_view.update_hero(game_state.player_state.hero_id)

        game_engine = GameEngine(game_state, self.ui_view.info_message)

        # We set up observers for gameEngine and gameState, since they are newly created in this scene. The player
        # state's observers (ui view) have already been setup in an earlier scene however.
        register_game_engine_observers(game_engine, self.ui_view)
        register_game_state_observers(game_state, self.ui_view, include_player_state=False)

        world_behavior = DungeonBehavior(self.scene_factory, game_state, self.ui_view.info_message)

        # Inventory has to be refreshed like this. Most item effects modify PlayerState, but movement speed effects are
        # applied to the hero WorldEntity (which is created anew with default movement speed in here).
        game_engine.set_item_inventory(item_inventory_slots)

        # Clear any messages to give space for any messages generated when entering the dungeon
        self.ui_view.info_message.clear_messages()

        # If we don't clear the minimap, there will be remains from the previous map
        self.ui_view.minimap.clear_exploration()

        playing_scene = self.scene_factory.playing_scene(
            game_state=game_state,
            game_engine=game_engine,
            world_behavior=world_behavior,
            ui_view=self.ui_view,
            new_hero_was_created=False,
            character_file=self.character_file,
            total_time_played_on_character=self.total_time_played_on_character)
        return SceneTransition(playing_scene)
