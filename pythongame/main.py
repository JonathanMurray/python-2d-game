import random
from typing import Optional

import pygame

from pythongame.core.common import SceneId, Millis
from pythongame.core.game_data import allocate_input_keys_for_abilities
from pythongame.core.game_engine import GameEngine
from pythongame.core.player_environment_interactions import PlayerInteractionsState
from pythongame.core.sound_player import init_sound_player
from pythongame.core.view import View
from pythongame.core.view_state import ViewState
from pythongame.map_file import create_game_state_from_json_file
from pythongame.register_game_data import register_all_game_data
from pythongame.scene_paused import PausedScene
from pythongame.scene_picking_hero import PickingHeroScene
from pythongame.scene_playing import PlayingScene

SCREEN_SIZE = (700, 700)
CAMERA_SIZE = (700, 530)

register_all_game_data()


def main(map_file_name: Optional[str], chosen_hero_id: Optional[str], hero_start_level: Optional[int],
         start_money: Optional[int], load_from_file: Optional[str]):
    map_file_name = map_file_name or "map1.json"

    # TODO Handle flags in combination with 'picking hero' scene
    # saved_player_state = load_player_state_from_json_file("savefiles/" + load_from_file) if load_from_file else None
    # if saved_player_state:
    #    hero_id = HeroId[saved_player_state.hero_id]
    # elif chosen_hero_id:
    #    hero_id = HeroId[chosen_hero_id]
    # else:
    #    hero_id = HeroId.MAGE
    # hero_start_level = int(hero_start_level) if hero_start_level else 1
    # start_money = int(start_money) if start_money else 0

    scene_id: SceneId = SceneId.PICKING_HERO

    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)
    init_sound_player()
    clock = pygame.time.Clock()

    picking_hero_scene = PickingHeroScene(view)
    # These scenes are initialized after hero has been picked
    playing_scene = None
    paused_scene = None

    # TODO Handle flags in combination with 'picking hero' scene
    # if saved_player_state:
    #    # TODO Move this somewhere else
    #    game_state.player_state.gain_exp_worth_n_levels(saved_player_state.level - 1)
    #    allocate_input_keys_for_abilities(game_state.player_state.abilities)
    #    game_state.player_state.gain_exp(saved_player_state.exp)
    #    game_engine.set_item_inventory([ItemType[item] if item else None for item in saved_player_state.items])
    #    game_state.player_state.consumable_inventory = ConsumableInventory(
    #        {int(slot_number): [ConsumableType[c] for c in consumables] for (slot_number, consumables)
    #         in saved_player_state.consumables_in_slots.items()}
    #    )
    #    game_state.player_state.money += saved_player_state.money
    #    for portal in game_state.portals:
    #        if portal.portal_id.name in saved_player_state.enabled_portals:
    #            sprite = saved_player_state.enabled_portals[portal.portal_id.name]
    #            portal.activate(Sprite[sprite])
    # else:
    #    if hero_start_level > 1:
    #        game_state.player_state.gain_exp_worth_n_levels(hero_start_level - 1)
    #        allocate_input_keys_for_abilities(game_state.player_state.abilities)
    #    if start_money > 0:
    #        game_state.player_state.money += start_money

    while True:

        clock.tick()
        time_passed = Millis(clock.get_time())

        if scene_id == SceneId.PICKING_HERO:
            picked_hero = picking_hero_scene.run_one_frame()
            if picked_hero is not None:
                game_state = create_game_state_from_json_file(CAMERA_SIZE, "resources/maps/" + map_file_name,
                                                              picked_hero)
                allocate_input_keys_for_abilities(game_state.player_state.abilities)
                view_state = ViewState(game_state.entire_world_area)
                game_engine = GameEngine(game_state, view_state)
                player_interactions_state = PlayerInteractionsState(view_state)
                playing_scene = PlayingScene(
                    player_interactions_state,
                    game_state,
                    game_engine,
                    view,
                    view_state)
                paused_scene = PausedScene(game_state, view, view_state)
                view_state.set_message("Hint: " + get_random_hint())
                scene_id = SceneId.PLAYING

        elif scene_id == SceneId.PLAYING:
            transition_to_pause = playing_scene.run_one_frame(time_passed, str(int(clock.get_fps())))
            if transition_to_pause:
                scene_id = SceneId.PAUSED

        elif scene_id == SceneId.PAUSED:
            transition_to_playing = paused_scene.run_one_frame()
            if transition_to_playing:
                scene_id = SceneId.PLAYING

        else:
            raise Exception("Unhandled scene: " + str(scene_id))


def get_random_hint():
    hints = [
        "Hold Shift to see more info about lootable items",
        "Press Space to interact with NPCs and objects",
        "Reaching certain levels unlocks new abilities",
        "Use the number keys for potions and other consumables",
        "Gold coins are looted by simply walking over them",
        "If you die, you'll respawn but lose exp points"
    ]
    return random.choice(hints)
