import sys
from typing import Tuple, Optional, List

import pygame

from pythongame.core.common import Direction, Sprite, sum_of_vectors
from pythongame.core.game_data import ENEMIES, WALL_SIZE, POTION_ENTITY_SPRITES
from pythongame.core.game_state import WorldEntity, Enemy, PotionOnGround
from pythongame.core.view import View
from pythongame.game_world_init import create_game_state_from_file, save_game_state_to_file, MapFileEntity, \
    MAP_FILE_ENTITIES_BY_CHAR
from pythongame.potion_health import POTION_ENTITY_SIZE
from pythongame.register_game_data import register_all_game_data

SCREEN_SIZE = (1200, 700)
CAMERA_SIZE = SCREEN_SIZE

register_all_game_data()


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
    camera_move_distance = grid_cell_size * 4
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
                        for potion in [p for p in game_state.potions_on_ground
                                       if p.world_entity.get_position() == snapped_mouse_world_position]:
                            game_state.potions_on_ground.remove(potion)

            if event.type == pygame.KEYDOWN:
                if event.unicode.upper() in MAP_FILE_ENTITIES_BY_CHAR:
                    placing_map_file_entity = MAP_FILE_ENTITIES_BY_CHAR[event.unicode.upper()]
                elif event.key == pygame.K_s:
                    save_file = map_file
                    save_game_state_to_file(game_state, save_file)
                    print("Saved state to " + save_file)
                elif event.key == pygame.K_RIGHT:
                    game_state.translate_camera_position((camera_move_distance, 0))
                elif event.key == pygame.K_DOWN:
                    game_state.translate_camera_position((0, camera_move_distance))
                elif event.key == pygame.K_LEFT:
                    game_state.translate_camera_position((-camera_move_distance, 0))
                elif event.key == pygame.K_UP:
                    game_state.translate_camera_position((0, -camera_move_distance))
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
                    elif placing_map_file_entity.potion_type:
                        sprite = POTION_ENTITY_SPRITES[placing_map_file_entity.potion_type]
                        entity = WorldEntity(snapped_mouse_world_position, POTION_ENTITY_SIZE, sprite)
                        game_state.potions_on_ground.append(PotionOnGround(entity, placing_map_file_entity.potion_type))

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
                entity = WorldEntity((0, 0), WALL_SIZE, Sprite.WALL)
                view.render_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif placing_map_file_entity.potion_type:
                sprite = POTION_ENTITY_SPRITES[placing_map_file_entity.potion_type]
                entity = WorldEntity((0, 0), POTION_ENTITY_SIZE, sprite)
                view.render_world_entity_at_position(entity, snapped_mouse_screen_position)
        else:
            snapped_mouse_rect = (snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                  grid_cell_size, grid_cell_size)
            view.render_map_editor_mouse_rect(snapped_mouse_rect)

        view.update_display()


if __name__ == "__main__":
    main()
