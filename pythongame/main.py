import sys

import pygame

from pythongame.ability_aoe_attack import register_aoe_attack_ability
from pythongame.ability_channel_attack import register_channel_attack_ability
from pythongame.ability_fireball import register_fireball_ability
from pythongame.ability_heal import register_heal_ability
from pythongame.ability_teleport import register_teleport_ability
from pythongame.core.common import Millis
from pythongame.core.game_engine import GameEngine
from pythongame.core.user_input import get_user_actions, ActionExitGame, ActionTryUseAbility, ActionTryUsePotion, \
    ActionMoveInDirection, ActionStopMoving, ActionPauseGame
from pythongame.core.view import View
from pythongame.core.view_state import ViewState
from pythongame.enemy_berserker import register_berserker_enemy
from pythongame.enemy_dumb import register_dumb_enemy
from pythongame.enemy_mage import register_mage_enemy
from pythongame.enemy_rat_1 import register_rat_1_enemy
from pythongame.enemy_rat_2 import register_rat_2_enemy
from pythongame.enemy_smart import register_smart_enemy
from pythongame.game_world_init import init_game_state_from_file
from pythongame.player_data import register_player_data
from pythongame.potion_health import register_health_potion
from pythongame.potion_invis import register_invis_potion
from pythongame.potion_mana import register_mana_potion
from pythongame.potion_speed import register_speed_potion

SCREEN_SIZE = (700, 600)
CAMERA_SIZE = (700, 400)

register_fireball_ability()
register_heal_ability()
register_aoe_attack_ability()
register_channel_attack_ability()
register_teleport_ability()
register_health_potion()
register_mana_potion()
register_invis_potion()
register_speed_potion()
register_dumb_enemy()
register_smart_enemy()
register_mage_enemy()
register_berserker_enemy()
register_player_data()
register_rat_1_enemy()
register_rat_2_enemy()


def main():
    game_state = init_game_state_from_file(CAMERA_SIZE)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)
    view_state = ViewState(game_state.game_world_size)
    clock = pygame.time.Clock()

    game_engine = GameEngine(game_state, view_state)

    is_paused = False

    while True:

        # ------------------------------------
        #         HANDLE USER INPUT
        # ------------------------------------

        user_actions = get_user_actions()
        for action in user_actions:
            if isinstance(action, ActionExitGame):
                pygame.quit()
                sys.exit()
            if not is_paused:
                if isinstance(action, ActionTryUseAbility):
                    game_engine.try_use_ability(action.ability_type)
                elif isinstance(action, ActionTryUsePotion):
                    game_engine.try_use_potion(action.slot_number)
                elif isinstance(action, ActionMoveInDirection):
                    game_engine.move_in_direction(action.direction)
                elif isinstance(action, ActionStopMoving):
                    game_engine.stop_moving()
            if isinstance(action, ActionPauseGame):
                is_paused = not is_paused

        # ------------------------------------
        #     UPDATE STATE BASED ON CLOCK
        # ------------------------------------

        clock.tick()
        time_passed = Millis(clock.get_time())

        if not is_paused:
            game_engine.run_one_frame(time_passed)

        # ------------------------------------
        #          RENDER EVERYTHING
        # ------------------------------------

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            enemies=game_state.enemies,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=False)

        view.render_ui(
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            player_mana=game_state.player_state.mana,
            player_max_mana=game_state.player_state.max_mana,
            potion_slots=game_state.player_state.potion_slots,
            player_active_buffs=game_state.player_state.active_buffs,
            fps_string=str(int(clock.get_fps())),
            player_minimap_relative_position=view_state.player_minimap_relative_position,
            abilities=game_state.player_state.abilities,
            message=view_state.message,
            highlighted_potion_action=view_state.highlighted_potion_action,
            highlighted_ability_action=view_state.highlighted_ability_action,
            is_paused=is_paused,
            ability_cooldowns_remaining=game_state.player_state.ability_cooldowns_remaining)

        view.update_display()


if __name__ == "__main__":
    main()
