import sys
from typing import Tuple, Optional

import pygame

from pythongame.ability_aoe_attack import register_aoe_attack_ability
from pythongame.ability_channel_attack import register_channel_attack_ability
from pythongame.ability_fireball import register_fireball_ability
from pythongame.ability_heal import register_heal_ability
from pythongame.ability_teleport import register_teleport_ability
from pythongame.core.common import EnemyType, Direction, Sprite
from pythongame.core.enemy_behavior import create_enemy_mind
from pythongame.core.game_data import ENEMIES, WALL_SIZE
from pythongame.core.game_state import WorldEntity, Enemy
from pythongame.core.view import View
from pythongame.enemy_berserker import register_berserker_enemy
from pythongame.enemy_dumb import register_dumb_enemy
from pythongame.enemy_mage import register_mage_enemy
from pythongame.enemy_rat_1 import register_rat_1_enemy
from pythongame.enemy_rat_2 import register_rat_2_enemy
from pythongame.enemy_smart import register_smart_enemy
from pythongame.game_world_init import create_game_state_from_file, save_game_state_to_file, MapFileEntity
from pythongame.player_data import register_player_data
from pythongame.potion_health import register_health_potion
from pythongame.potion_invis import register_invis_potion
from pythongame.potion_mana import register_mana_potion
from pythongame.potion_speed import register_speed_potion

MAP_FILE = "resources/maps/demo.txt"

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
    game_state = create_game_state_from_file(CAMERA_SIZE, MAP_FILE)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)

    placing_map_file_entity: Optional[MapFileEntity] = None

    grid_cell_size = 25
    snapped_mouse_position = (0, 0)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                exact_mouse_position: Tuple[int, int] = event.pos
                snapped_mouse_position = ((exact_mouse_position[0] // grid_cell_size) * grid_cell_size,
                                          (exact_mouse_position[1] // grid_cell_size) * grid_cell_size)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    placing_map_file_entity = MapFileEntity(None, True, False)
                elif event.key == pygame.K_r:
                    placing_map_file_entity = MapFileEntity(EnemyType.RAT_1, False, False)
                elif event.key == pygame.K_2:
                    placing_map_file_entity = MapFileEntity(EnemyType.RAT_2, False, False)
                elif event.key == pygame.K_x:
                    placing_map_file_entity = MapFileEntity(None, False, True)
                elif event.key == pygame.K_s:
                    save_file = MAP_FILE
                    save_game_state_to_file(game_state, save_file)
                    print("Saved state to " + save_file)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if placing_map_file_entity:
                    if placing_map_file_entity.is_player:
                        game_state.player_entity.set_position(snapped_mouse_position)
                    elif placing_map_file_entity.enemy_type:
                        enemy_type = placing_map_file_entity.enemy_type
                        data = ENEMIES[enemy_type]
                        entity = WorldEntity(snapped_mouse_position, data.size, data.sprite, Direction.DOWN,
                                             data.speed)
                        enemy = Enemy(enemy_type, entity, data.max_health, data.max_health,
                                      create_enemy_mind(enemy_type))
                        game_state.enemies.append(enemy)
                    elif placing_map_file_entity.is_wall:
                        game_state.add_wall(WorldEntity(snapped_mouse_position, WALL_SIZE, Sprite.WALL))

        view.render_world(
            all_entities_to_render=game_state.get_all_entities_to_render(),
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            enemies=game_state.enemies,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=True)

        if placing_map_file_entity:
            if placing_map_file_entity.enemy_type:
                data = ENEMIES[placing_map_file_entity.enemy_type]
                entity = WorldEntity((0, 0), data.size, data.sprite, Direction.DOWN, data.speed)
                view.render_mapmaker_world_entity(entity, snapped_mouse_position)
            elif placing_map_file_entity.is_player:
                view.render_mapmaker_world_entity(game_state.player_entity, snapped_mouse_position)
            elif placing_map_file_entity.is_wall:
                entity = WorldEntity((0, 0), WALL_SIZE, Sprite.WALL, Direction.DOWN, 0)
                view.render_mapmaker_world_entity(entity, snapped_mouse_position)
        else:
            snapped_mouse_rect = (snapped_mouse_position[0], snapped_mouse_position[1], grid_cell_size, grid_cell_size)
            view.render_mouse_selection_rect(snapped_mouse_rect)

        view.update_display()


if __name__ == "__main__":
    main()
