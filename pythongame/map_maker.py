import sys
from typing import Tuple

import pygame

from pythongame.ability_aoe_attack import register_aoe_attack_ability
from pythongame.ability_channel_attack import register_channel_attack_ability
from pythongame.ability_fireball import register_fireball_ability
from pythongame.ability_heal import register_heal_ability
from pythongame.ability_teleport import register_teleport_ability
from pythongame.core.view import View
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

    is_placing_player_entity = False

    grid_cell_size = 25
    mouse_selection_rect = (0, 0, grid_cell_size, grid_cell_size)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                mouse_position: Tuple[int, int] = event.pos
                mouse_selection_rect = ((mouse_position[0] // grid_cell_size) * grid_cell_size,
                                        (mouse_position[1] // grid_cell_size) * grid_cell_size,
                                        grid_cell_size,
                                        grid_cell_size)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    is_placing_player_entity = not is_placing_player_entity

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            enemies=game_state.enemies,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=True)

        if is_placing_player_entity:
            view.render_mapmaker_world_entity(game_state.player_entity,
                                              (mouse_selection_rect[0], mouse_selection_rect[1]))
        else:
            view.render_mouse_selection_rect(mouse_selection_rect)

        view.update_display()


if __name__ == "__main__":
    main()
