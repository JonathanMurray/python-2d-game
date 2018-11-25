import sys
from typing import Tuple, Optional, List

import pygame

from pythongame.ability_aoe_attack import register_aoe_attack_ability
from pythongame.ability_channel_attack import register_channel_attack_ability
from pythongame.ability_fireball import register_fireball_ability
from pythongame.ability_heal import register_heal_ability
from pythongame.ability_teleport import register_teleport_ability
from pythongame.core.common import EnemyType, Direction, Sprite, sum_of_vectors
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

SCREEN_SIZE = (1200, 700)
CAMERA_SIZE = SCREEN_SIZE

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


def main(args: List[str]):
    if len(args) == 1:
        map_file = args[0]
    else:
        map_file = "resources/maps/demo.txt"

    game_state = create_game_state_from_file(CAMERA_SIZE, map_file)
    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)

    # Deleting entities when this is = None
    placing_map_file_entity: Optional[MapFileEntity] = None

    is_mouse_button_down = False

    grid_cell_size = 25
    snapped_mouse_screen_position = (0, 0)
    snapped_mouse_world_position = (0, 0)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                exact_mouse_screen_position: Tuple[int, int] = event.pos
                snapped_mouse_screen_position = ((exact_mouse_screen_position[0] // grid_cell_size) * grid_cell_size,
                                                 (exact_mouse_screen_position[1] // grid_cell_size) * grid_cell_size)
                snapped_mouse_world_position = sum_of_vectors(
                    snapped_mouse_screen_position, game_state.camera_world_area.get_position())
                if is_mouse_button_down:
                    if placing_map_file_entity and placing_map_file_entity.is_wall:
                        already_has_wall = any([w for w in game_state.walls
                                                if w.get_position() == snapped_mouse_world_position])
                        if not already_has_wall:
                            game_state.add_wall(WorldEntity(snapped_mouse_world_position, WALL_SIZE, Sprite.WALL))
                    else:
                        # delete entities
                        for wall in [w for w in game_state.walls if w.get_position() == snapped_mouse_world_position]:
                            game_state.remove_wall(wall)
                        for enemy in [e for e in game_state.enemies if
                                      e.world_entity.get_position() == snapped_mouse_world_position]:
                            game_state.enemies.remove(enemy)

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
                    save_file = map_file
                    save_game_state_to_file(game_state, save_file)
                    print("Saved state to " + save_file)
                elif event.key == pygame.K_RIGHT:
                    game_state.translate_camera_position((grid_cell_size, 0))
                elif event.key == pygame.K_DOWN:
                    game_state.translate_camera_position((0, grid_cell_size))
                elif event.key == pygame.K_LEFT:
                    game_state.translate_camera_position((-grid_cell_size, 0))
                elif event.key == pygame.K_UP:
                    game_state.translate_camera_position((0, -grid_cell_size))
                elif event.key == pygame.K_q:
                    # Used for deleting entities
                    placing_map_file_entity = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                is_mouse_button_down = True
                if placing_map_file_entity:
                    if placing_map_file_entity.is_player:
                        game_state.player_entity.set_position(snapped_mouse_world_position)
                    elif placing_map_file_entity.enemy_type:
                        enemy_type = placing_map_file_entity.enemy_type
                        data = ENEMIES[enemy_type]
                        entity = WorldEntity(snapped_mouse_world_position, data.size, data.sprite, Direction.DOWN,
                                             data.speed)
                        enemy = Enemy(enemy_type, entity, data.max_health, data.max_health, None)
                        game_state.enemies.append(enemy)
                    elif placing_map_file_entity.is_wall:
                        game_state.add_wall(WorldEntity(snapped_mouse_world_position, WALL_SIZE, Sprite.WALL))

            if event.type == pygame.MOUSEBUTTONUP:
                is_mouse_button_down = False

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
                view.render_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif placing_map_file_entity.is_player:
                view.render_world_entity_at_position(game_state.player_entity, snapped_mouse_screen_position)
            elif placing_map_file_entity.is_wall:
                entity = WorldEntity((0, 0), WALL_SIZE, Sprite.WALL, Direction.DOWN, 0)
                view.render_world_entity_at_position(entity, snapped_mouse_screen_position)
        else:
            snapped_mouse_rect = (snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                  grid_cell_size, grid_cell_size)
            view.render_map_editor_mouse_rect(snapped_mouse_rect)

        view.update_display()


if __name__ == "__main__":
    main()
