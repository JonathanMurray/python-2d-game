import sys
from pathlib import Path
from typing import Tuple, Optional, List

import pygame
from pygame.rect import Rect

from generate_dungeon import generate_random_map_as_json
from pythongame.core.common import Sprite, WallType, NpcType, ConsumableType, ItemType, PortalId, HeroId, PeriodicTimer, \
    Millis
from pythongame.core.entity_creation import create_portal, create_hero_world_entity, create_npc, create_wall, \
    create_consumable_on_ground, create_item_on_ground, create_decoration_entity, create_money_pile_on_ground, \
    create_player_state, create_chest
from pythongame.core.game_data import ENTITY_SPRITE_INITIALIZERS, UI_ICON_SPRITE_PATHS, PORTRAIT_ICON_SPRITE_PATHS
from pythongame.core.game_state import GameState
from pythongame.core.math import sum_of_vectors, get_relative_pos_within_rect
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.image_loading import load_images_by_sprite, load_images_by_ui_sprite, \
    load_images_by_portrait_sprite
from pythongame.map_editor.map_editor_ui_view import MapEditorView, PORTRAIT_ICON_SIZE, MAP_EDITOR_UI_ICON_SIZE, \
    EntityTab, GenerateRandomMap, SetCameraPosition
from pythongame.map_editor.map_editor_world_entity import MapEditorWorldEntity
from pythongame.map_file import save_game_state_to_json_file, create_game_state_from_json_file, \
    create_game_state_from_map_data
from pythongame.register_game_data import register_all_game_data

MAP_DIR = "resources/maps/"

register_all_game_data()

WALL_ENTITIES = [MapEditorWorldEntity.wall(wall_type) for wall_type in WallType]
NPC_ENTITIES = [MapEditorWorldEntity.npc(npc_type) for npc_type in NpcType]
PORTAL_ENTITIES = [MapEditorWorldEntity.portal(portal_id) for portal_id in PortalId]
CONSUMABLE_ENTITIES = [MapEditorWorldEntity.consumable(consumable_type) for consumable_type in ConsumableType]
ITEM_ENTITIES = [MapEditorWorldEntity.item(item_type) for item_type in ItemType]

MISC_ENTITIES: List[MapEditorWorldEntity] = [
    MapEditorWorldEntity.player(),
    MapEditorWorldEntity.chest(),
    MapEditorWorldEntity.money(1),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE_GRAY),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_PLANT),
]

SCREEN_SIZE = (1200, 750)
CAMERA_SIZE = (1200, 550)

# The choice of hero shouldn't matter in the map editor, as we only store its position in the map file
HERO_ID = HeroId.MAGE


class UserState:
    def __init__(self, placing_entity: Optional[MapEditorWorldEntity], deleting_entities: bool,
                 deleting_decorations: bool):
        self.placing_entity = placing_entity
        self.deleting_entities = deleting_entities
        self.deleting_decorations = deleting_decorations

    @staticmethod
    def placing_entity(entity: MapEditorWorldEntity):
        return UserState(entity, False, False)

    @staticmethod
    def deleting_entities():
        return UserState(None, True, False)

    @staticmethod
    def deleting_decorations():
        return UserState(None, False, True)


def main(map_file_name: Optional[str]):
    map_file_path = MAP_DIR + (map_file_name or "map1.json")

    if Path(map_file_path).exists():
        game_state = create_game_state_from_json_file(CAMERA_SIZE, map_file_path, HERO_ID)
    else:
        player_entity = create_hero_world_entity(HERO_ID, (0, 0))
        player_state = create_player_state(HERO_ID)
        game_state = GameState(player_entity, [], [], [], [], [], CAMERA_SIZE, Rect(-250, -250, 500, 500),
                               player_state, [], [], [])

    pygame.init()

    pygame_screen = pygame.display.set_mode(SCREEN_SIZE)
    images_by_sprite = load_images_by_sprite(ENTITY_SPRITE_INITIALIZERS)
    images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, MAP_EDITOR_UI_ICON_SIZE)
    images_by_portrait_sprite = load_images_by_portrait_sprite(PORTRAIT_ICON_SPRITE_PATHS, PORTRAIT_ICON_SIZE)
    world_view = GameWorldView(pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite)
    world_area_aspect_ratio = (game_state.entire_world_area.w, game_state.entire_world_area.h)
    ui_view = MapEditorView(pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite, images_by_ui_sprite,
                            images_by_portrait_sprite, world_area_aspect_ratio)

    user_state = UserState.deleting_entities()

    is_mouse_button_down = False

    possible_grid_cell_sizes = [25, 50]
    grid_cell_size_index = 0
    grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]

    camera_move_distance = 75  # must be a multiple of the grid size
    snapped_mouse_screen_position = (0, 0)
    snapped_mouse_world_position = (0, 0)
    exact_mouse_screen_position = (0, 0)
    is_snapped_mouse_within_world = True
    is_snapped_mouse_over_ui = False

    game_state.center_camera_on_player()
    game_state.snap_camera_to_grid(grid_cell_size)
    game_state.camera_world_area.topleft = ((game_state.camera_world_area.x // grid_cell_size) * grid_cell_size,
                                            (game_state.camera_world_area.y // grid_cell_size) * grid_cell_size)

    held_down_arrow_keys = set([])
    clock = pygame.time.Clock()
    camera_pan_timer = PeriodicTimer(Millis(50))

    shown_tab = EntityTab.ITEMS

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                exact_mouse_screen_position: Tuple[int, int] = event.pos
                ui_view.handle_mouse_movement(exact_mouse_screen_position)
                snapped_mouse_screen_position = ((exact_mouse_screen_position[0] // grid_cell_size) * grid_cell_size,
                                                 (exact_mouse_screen_position[1] // grid_cell_size) * grid_cell_size)
                snapped_mouse_world_position = sum_of_vectors(
                    snapped_mouse_screen_position, game_state.camera_world_area.topleft)
                is_snapped_mouse_within_world = game_state.is_position_within_game_world(snapped_mouse_world_position)
                is_snapped_mouse_over_ui = ui_view.is_screen_position_within_ui(snapped_mouse_screen_position)
                if is_mouse_button_down and is_snapped_mouse_within_world and not is_snapped_mouse_over_ui:
                    if user_state.placing_entity:
                        if user_state.placing_entity.wall_type:
                            _add_wall(game_state, snapped_mouse_world_position, user_state.placing_entity.wall_type)
                        elif user_state.placing_entity.decoration_sprite:
                            _add_decoration(user_state.placing_entity.decoration_sprite, game_state,
                                            snapped_mouse_world_position)
                    elif user_state.deleting_entities:
                        _delete_map_entities_from_position(game_state, snapped_mouse_world_position)
                    else:
                        _delete_map_decorations_from_position(game_state, snapped_mouse_world_position)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    save_file = map_file_path
                    save_game_state_to_json_file(game_state, save_file)
                    print("Saved state to " + save_file)
                elif event.key in [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]:
                    held_down_arrow_keys.add(event.key)
                elif event.key == pygame.K_q:
                    user_state = UserState.deleting_entities()
                elif event.key == pygame.K_z:
                    user_state = UserState.deleting_decorations()
                elif event.key == pygame.K_PLUS:
                    grid_cell_size_index = (grid_cell_size_index + 1) % len(possible_grid_cell_sizes)
                    grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]
                elif event.key == pygame.K_v:
                    shown_tab = EntityTab.ITEMS
                elif event.key == pygame.K_b:
                    shown_tab = EntityTab.NPCS
                elif event.key == pygame.K_n:
                    shown_tab = EntityTab.WALLS
                elif event.key == pygame.K_m:
                    shown_tab = EntityTab.MISC

            if event.type == pygame.KEYUP:
                if event.key in held_down_arrow_keys:
                    held_down_arrow_keys.remove(event.key)

            if event.type == pygame.MOUSEBUTTONDOWN:
                event_from_ui = ui_view.handle_mouse_click()
                if event_from_ui:
                    if isinstance(event_from_ui, GenerateRandomMap):
                        map_json = generate_random_map_as_json()
                        game_state = create_game_state_from_map_data(CAMERA_SIZE, map_json, HERO_ID)
                        game_state.center_camera_on_player()
                        game_state.snap_camera_to_grid(grid_cell_size)
                        aspect_ratio = (game_state.entire_world_area.w, game_state.entire_world_area.h)
                        ui_view.on_world_area_aspect_ratio_updated(aspect_ratio)
                    elif isinstance(event_from_ui, SetCameraPosition):
                        game_state.set_camera_position_to_ratio_of_world(event_from_ui.position_ratio)
                        game_state.snap_camera_to_grid(grid_cell_size)
                    else:
                        raise Exception("Unhandled event: " + str(event_from_ui))

                is_mouse_button_down = True
                if user_state.placing_entity:
                    entity_being_placed = user_state.placing_entity
                    if is_snapped_mouse_within_world and not is_snapped_mouse_over_ui:
                        if entity_being_placed.is_player:
                            game_state.player_entity.set_position(snapped_mouse_world_position)
                        elif entity_being_placed.npc_type:
                            _add_npc(entity_being_placed.npc_type, game_state, snapped_mouse_world_position)
                        elif entity_being_placed.wall_type:
                            _add_wall(game_state, snapped_mouse_world_position, entity_being_placed.wall_type)
                        elif entity_being_placed.consumable_type:
                            _add_consumable(entity_being_placed.consumable_type, game_state,
                                            snapped_mouse_world_position)
                        elif entity_being_placed.item_type:
                            _add_item(entity_being_placed.item_type, game_state, snapped_mouse_world_position)
                        elif entity_being_placed.decoration_sprite:
                            _add_decoration(entity_being_placed.decoration_sprite, game_state,
                                            snapped_mouse_world_position)
                        elif entity_being_placed.money_amount:
                            _add_money(entity_being_placed.money_amount, game_state, snapped_mouse_world_position)
                        elif entity_being_placed.portal_id:
                            _add_portal(entity_being_placed.portal_id, game_state, snapped_mouse_world_position)
                        elif entity_being_placed.is_chest:
                            _add_chest(game_state, snapped_mouse_world_position)
                        else:
                            raise Exception("Unknown entity: " + str(entity_being_placed))
                elif user_state.deleting_entities:
                    _delete_map_entities_from_position(game_state, snapped_mouse_world_position)
                else:
                    _delete_map_decorations_from_position(game_state, snapped_mouse_world_position)

            if event.type == pygame.MOUSEBUTTONUP:
                is_mouse_button_down = False

        clock.tick()
        time_passed = clock.get_time()

        if camera_pan_timer.update_and_check_if_ready(time_passed):
            if pygame.K_RIGHT in held_down_arrow_keys:
                game_state.translate_camera_position((camera_move_distance, 0))
            if pygame.K_LEFT in held_down_arrow_keys:
                game_state.translate_camera_position((-camera_move_distance, 0))
            if pygame.K_DOWN in held_down_arrow_keys:
                game_state.translate_camera_position((0, camera_move_distance))
            if pygame.K_UP in held_down_arrow_keys:
                game_state.translate_camera_position((0, -camera_move_distance))

        entities_to_render = game_state.get_all_entities_to_render()
        decorations_to_render = game_state.get_decorations_to_render()
        world_view.render_world(
            all_entities_to_render=entities_to_render,
            decorations_to_render=decorations_to_render,
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            player_active_buffs=game_state.player_state.active_buffs,
            camera_world_area=game_state.camera_world_area,
            non_player_characters=game_state.non_player_characters,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=ui_view.checkbox_show_entity_outlines.checked,
            player_health=game_state.player_state.health_resource.value,
            player_max_health=game_state.player_state.health_resource.max_value,
            entire_world_area=game_state.entire_world_area,
            entity_action_text=None)

        camera_world_area = game_state.camera_world_area
        world_area = game_state.entire_world_area
        camera_rect_ratio = ((camera_world_area.x - world_area.x) / world_area.w,
                             (camera_world_area.y - world_area.y) / world_area.h,
                             camera_world_area.w / world_area.w,
                             camera_world_area.h / world_area.h)

        npc_positions_ratio = [((npc.world_entity.x - world_area.x) / world_area.w,
                                (npc.world_entity.y - world_area.y) / world_area.h)
                               for npc in game_state.non_player_characters]
        wall_positions_ratio = [((wall.world_entity.x - world_area.x) / world_area.w,
                                 (wall.world_entity.y - world_area.y) / world_area.h)
                                for wall in game_state.walls_state.walls]

        if shown_tab == EntityTab.ITEMS:
            shown_entities = ITEM_ENTITIES
        elif shown_tab == EntityTab.NPCS:
            shown_entities = NPC_ENTITIES
        elif shown_tab == EntityTab.WALLS:
            shown_entities = WALL_ENTITIES
        elif shown_tab == EntityTab.MISC:
            shown_entities = MISC_ENTITIES
        else:
            raise Exception("Unknown entity tab: " + str(shown_tab))

        ui_view.set_shown_tab(shown_tab)

        relative_player_pos = get_relative_pos_within_rect(
            game_state.player_entity.get_position(), game_state.entire_world_area)
        entity_icon_hovered_by_mouse = ui_view.render(
            entities=shown_entities,
            placing_entity=user_state.placing_entity,
            deleting_entities=user_state.deleting_entities,
            deleting_decorations=user_state.deleting_decorations,
            num_enemies=len(game_state.non_player_characters),
            num_walls=len(game_state.walls_state.walls),
            num_decorations=len(game_state.decorations_state.decoration_entities),
            grid_cell_size=grid_cell_size,
            mouse_screen_position=exact_mouse_screen_position,
            camera_rect_ratio=camera_rect_ratio,
            npc_positions_ratio=npc_positions_ratio,
            wall_positions_ratio=wall_positions_ratio,
            relative_player_position=relative_player_pos)

        if is_mouse_button_down and entity_icon_hovered_by_mouse:
            user_state = UserState.placing_entity(entity_icon_hovered_by_mouse)

        if is_snapped_mouse_over_ui:
            pass
            # render nothing over UI
        elif not is_snapped_mouse_within_world:
            snapped_mouse_rect = Rect(snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                      grid_cell_size, grid_cell_size)
            ui_view.render_map_editor_mouse_rect((250, 50, 0), snapped_mouse_rect)
        elif user_state.placing_entity:
            entity_being_placed = user_state.placing_entity
            ui_view.render_map_editor_world_entity_at_position(
                entity_being_placed.sprite, entity_being_placed.entity_size, snapped_mouse_screen_position)
        elif user_state.deleting_entities:
            snapped_mouse_rect = Rect(snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                      grid_cell_size, grid_cell_size)
            ui_view.render_map_editor_mouse_rect((250, 250, 0), snapped_mouse_rect)
        elif user_state.deleting_decorations:
            snapped_mouse_rect = Rect(snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                      grid_cell_size, grid_cell_size)
            ui_view.render_map_editor_mouse_rect((0, 250, 250), snapped_mouse_rect)
        else:
            raise Exception("Unhandled user_state: " + str(user_state))

        pygame.display.update()


def _add_money(amount: int, game_state, snapped_mouse_world_position):
    already_has_money = any([x for x in game_state.money_piles_on_ground
                             if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_money:
        money_pile_on_ground = create_money_pile_on_ground(amount, snapped_mouse_world_position)
        game_state.money_piles_on_ground.append(money_pile_on_ground)


def _add_portal(portal_id: PortalId, game_state, snapped_mouse_world_position):
    already_has_portal = any([x for x in game_state.portals
                              if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_portal:
        portal = create_portal(portal_id, snapped_mouse_world_position)
        game_state.portals.append(portal)


def _add_chest(game_state: GameState, snapped_mouse_world_position):
    already_has_chest = any([x for x in game_state.chests
                             if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_chest:
        chest = create_chest(snapped_mouse_world_position)
        game_state.chests.append(chest)


def _add_item(item_type: ItemType, game_state, snapped_mouse_world_position):
    already_has_item = any([x for x in game_state.items_on_ground
                            if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_item:
        item_on_ground = create_item_on_ground(item_type, snapped_mouse_world_position)
        game_state.items_on_ground.append(item_on_ground)


def _add_consumable(consumable_type: ConsumableType, game_state, snapped_mouse_world_position):
    already_has_consumable = any([x for x in game_state.consumables_on_ground
                                  if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_consumable:
        consumable_on_ground = create_consumable_on_ground(consumable_type, snapped_mouse_world_position)
        game_state.consumables_on_ground.append(consumable_on_ground)


def _add_npc(npc_type, game_state: GameState, snapped_mouse_world_position):
    already_has_npc = any([x for x in game_state.non_player_characters
                           if x.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_npc:
        npc = create_npc(npc_type, snapped_mouse_world_position)
        game_state.add_non_player_character(npc)


def _add_decoration(decoration_sprite: Sprite, game_state: GameState, snapped_mouse_world_position):
    if len(game_state.decorations_state.get_decorations_at_position(snapped_mouse_world_position)) == 0:
        decoration_entity = create_decoration_entity(snapped_mouse_world_position, decoration_sprite)
        game_state.decorations_state.add_decoration(decoration_entity)


def _add_wall(game_state, snapped_mouse_world_position: Tuple[int, int], wall_type: WallType):
    if len(game_state.walls_state.get_walls_at_position(snapped_mouse_world_position)) == 0:
        wall = create_wall(wall_type, snapped_mouse_world_position)
        game_state.walls_state.add_wall(wall)


def _delete_map_entities_from_position(game_state: GameState, snapped_mouse_world_position: Tuple[int, int]):
    for wall in game_state.walls_state.get_walls_at_position(snapped_mouse_world_position):
        game_state.walls_state.remove_wall(wall)
    for enemy in [e for e in game_state.non_player_characters if
                  e.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.non_player_characters.remove(enemy)
    for consumable in [p for p in game_state.consumables_on_ground
                       if p.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.consumables_on_ground.remove(consumable)
    for item in [i for i in game_state.items_on_ground
                 if i.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.items_on_ground.remove(item)
    for money_pile in [m for m in game_state.money_piles_on_ground
                       if m.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.money_piles_on_ground.remove(money_pile)
    for portal in [p for p in game_state.portals
                   if p.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.portals.remove(portal)


def _delete_map_decorations_from_position(game_state: GameState, snapped_mouse_world_position: Tuple[int, int]):
    for d in game_state.decorations_state.get_decorations_at_position(snapped_mouse_world_position):
        game_state.decorations_state.remove_decoration(d)
