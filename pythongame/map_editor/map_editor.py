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
from pythongame.core.view.game_world_view import GameWorldView
from pythongame.core.view.image_loading import load_images_by_sprite, load_images_by_ui_sprite, \
    load_images_by_portrait_sprite
from pythongame.map_editor.map_editor_ui_view import MapEditorView, PORTRAIT_ICON_SIZE, MAP_EDITOR_UI_ICON_SIZE, \
    EntityTab, GenerateRandomMap, SetCameraPosition, AddEntity, DeleteEntities, DeleteDecorations, MapEditorAction, \
    SaveMap
from pythongame.map_editor.map_editor_world_entity import MapEditorWorldEntity
from pythongame.map_file import save_game_state_to_json_file, create_game_state_from_json_file, \
    create_game_state_from_map_data
from pythongame.register_game_data import register_all_game_data

MAP_DIR = "resources/maps/"

register_all_game_data()

WALL_ENTITIES = [MapEditorWorldEntity.wall(wall_type) for wall_type in WallType]
NPC_ENTITIES = [MapEditorWorldEntity.npc(npc_type) for npc_type in NpcType]
ITEM_ENTITIES = [MapEditorWorldEntity.item(item_type) for item_type in ItemType]
MISC_ENTITIES: List[MapEditorWorldEntity] = \
    [
        MapEditorWorldEntity.player(),
        MapEditorWorldEntity.chest(),
        MapEditorWorldEntity.money(1),
        MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE),
        MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE_GRAY),
        MapEditorWorldEntity.decoration(Sprite.DECORATION_PLANT),
    ] + \
    [MapEditorWorldEntity.consumable(consumable_type) for consumable_type in ConsumableType] + \
    [MapEditorWorldEntity.portal(portal_id) for portal_id in PortalId]

ENTITIES_BY_TYPE = {
    EntityTab.ITEMS: ITEM_ENTITIES,
    EntityTab.NPCS: NPC_ENTITIES,
    EntityTab.WALLS: WALL_ENTITIES,
    EntityTab.MISC: MISC_ENTITIES
}

SCREEN_SIZE = (1200, 750)
CAMERA_SIZE = (1200, 550)

# The choice of hero shouldn't matter in the map editor, as we only store its position in the map file
HERO_ID = HeroId.MAGE


class MapEditor:
    def __init__(self, map_file_name: Optional[str]):
        self.map_file_path = MAP_DIR + (map_file_name or "map1.json")

        if Path(self.map_file_path).exists():
            self.game_state = create_game_state_from_json_file(CAMERA_SIZE, self.map_file_path, HERO_ID)
        else:
            player_entity = create_hero_world_entity(HERO_ID, (0, 0))
            player_state = create_player_state(HERO_ID)
            self.game_state = GameState(player_entity, [], [], [], [], [], CAMERA_SIZE, Rect(-250, -250, 500, 500),
                                        player_state, [], [], [])

        pygame.init()

        pygame_screen = pygame.display.set_mode(SCREEN_SIZE)
        images_by_sprite = load_images_by_sprite(ENTITY_SPRITE_INITIALIZERS)
        images_by_ui_sprite = load_images_by_ui_sprite(UI_ICON_SPRITE_PATHS, MAP_EDITOR_UI_ICON_SIZE)
        images_by_portrait_sprite = load_images_by_portrait_sprite(PORTRAIT_ICON_SPRITE_PATHS, PORTRAIT_ICON_SIZE)
        world_view = GameWorldView(pygame_screen, CAMERA_SIZE, SCREEN_SIZE, images_by_sprite)

        possible_grid_cell_sizes = [25, 50]
        grid_cell_size_index = 0
        grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]

        self.game_state.center_camera_on_player()
        self.game_state.snap_camera_to_grid(grid_cell_size)

        ui_view = MapEditorView(
            pygame_screen, self.game_state.camera_world_area, SCREEN_SIZE, images_by_sprite, images_by_ui_sprite,
            images_by_portrait_sprite, self.game_state.entire_world_area,
            self.game_state.player_entity.get_center_position(),
            ENTITIES_BY_TYPE, grid_cell_size, self.map_file_path)

        camera_move_distance = 75  # must be a multiple of the grid size

        held_down_arrow_keys = set([])
        clock = pygame.time.Clock()
        camera_pan_timer = PeriodicTimer(Millis(50))

        while True:

            # HANDLE USER INPUT

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEMOTION:
                    action = ui_view.handle_mouse_movement(event.pos)
                    if action:
                        self._handle_action(action, grid_cell_size)

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save()
                    elif event.key in [pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]:
                        held_down_arrow_keys.add(event.key)
                    elif event.key == pygame.K_PLUS:
                        grid_cell_size_index = (grid_cell_size_index + 1) % len(possible_grid_cell_sizes)
                        grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]
                        ui_view.grid_cell_size = grid_cell_size
                    else:
                        ui_view.handle_key_down(event.key)

                if event.type == pygame.KEYUP:
                    if event.key in held_down_arrow_keys:
                        held_down_arrow_keys.remove(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    action = ui_view.handle_mouse_click()
                    if action:
                        self._handle_action(action, grid_cell_size)

                elif event.type == pygame.MOUSEBUTTONUP:
                    ui_view.handle_mouse_release()

            # HANDLE TIME

            clock.tick()
            time_passed = clock.get_time()

            if camera_pan_timer.update_and_check_if_ready(time_passed):
                if pygame.K_RIGHT in held_down_arrow_keys:
                    self.game_state.translate_camera_position((camera_move_distance, 0))
                if pygame.K_LEFT in held_down_arrow_keys:
                    self.game_state.translate_camera_position((-camera_move_distance, 0))
                if pygame.K_DOWN in held_down_arrow_keys:
                    self.game_state.translate_camera_position((0, camera_move_distance))
                if pygame.K_UP in held_down_arrow_keys:
                    self.game_state.translate_camera_position((0, -camera_move_distance))

            ui_view.camera_world_area = self.game_state.camera_world_area
            ui_view.world_area = self.game_state.entire_world_area

            # RENDER

            world_view.render_world(
                all_entities_to_render=self.game_state.get_all_entities_to_render(),
                decorations_to_render=self.game_state.get_decorations_to_render(),
                player_entity=self.game_state.player_entity,
                is_player_invisible=self.game_state.player_state.is_invisible,
                player_active_buffs=self.game_state.player_state.active_buffs,
                camera_world_area=self.game_state.camera_world_area,
                non_player_characters=self.game_state.non_player_characters,
                visual_effects=self.game_state.visual_effects,
                render_hit_and_collision_boxes=ui_view._checkbox_show_entity_outlines.checked,
                player_health=self.game_state.player_state.health_resource.value,
                player_max_health=self.game_state.player_state.health_resource.max_value,
                entire_world_area=self.game_state.entire_world_area,
                entity_action_text=None)

            wall_positions = [w.world_entity.get_position() for w in self.game_state.walls_state.walls]
            npc_positions = [npc.world_entity.get_position() for npc in self.game_state.non_player_characters]

            ui_view.render(
                num_enemies=len(self.game_state.non_player_characters),
                num_walls=len(self.game_state.walls_state.walls),
                num_decorations=len(self.game_state.decorations_state.decoration_entities),
                npc_positions=npc_positions,
                wall_positions=wall_positions,
                player_position=self.game_state.player_entity.get_center_position())

            pygame.display.flip()

    def save(self):
        save_game_state_to_json_file(self.game_state, self.map_file_path)
        print("Saved state to " + self.map_file_path)

    def _handle_action(self, action: MapEditorAction, grid_cell_size: int):
        if isinstance(action, GenerateRandomMap):
            map_json = generate_random_map_as_json()
            self.game_state = create_game_state_from_map_data(CAMERA_SIZE, map_json, HERO_ID)
            self.game_state.center_camera_on_player()
            self.game_state.snap_camera_to_grid(grid_cell_size)
        elif isinstance(action, SaveMap):
            self.save()
        elif isinstance(action, SetCameraPosition):
            self.game_state.set_camera_position_to_ratio_of_world(action.position_ratio)
            self.game_state.snap_camera_to_grid(grid_cell_size)
        elif isinstance(action, AddEntity):
            entity_being_placed = action.entity
            if entity_being_placed.is_player:
                self.game_state.player_entity.set_position(action.world_position)
            elif entity_being_placed.npc_type:
                _add_npc(entity_being_placed.npc_type, self.game_state, action.world_position)
            elif entity_being_placed.wall_type:
                _add_wall(self.game_state, action.world_position, entity_being_placed.wall_type)
            elif entity_being_placed.consumable_type:
                _add_consumable(entity_being_placed.consumable_type, self.game_state,
                                action.world_position)
            elif entity_being_placed.item_type:
                _add_item(entity_being_placed.item_type, self.game_state, action.world_position)
            elif entity_being_placed.decoration_sprite:
                _add_decoration(entity_being_placed.decoration_sprite, self.game_state,
                                action.world_position)
            elif entity_being_placed.money_amount:
                _add_money(entity_being_placed.money_amount, self.game_state, action.world_position)
            elif entity_being_placed.portal_id:
                _add_portal(entity_being_placed.portal_id, self.game_state, action.world_position)
            elif entity_being_placed.is_chest:
                _add_chest(self.game_state, action.world_position)
            else:
                raise Exception("Unknown entity: " + str(entity_being_placed))
        elif isinstance(action, DeleteEntities):
            _delete_map_entities_from_position(self.game_state, action.world_position)
        elif isinstance(action, DeleteDecorations):
            _delete_map_decorations_from_position(self.game_state, action.world_position)
        else:
            raise Exception("Unhandled event: " + str(action))


def main(map_file_name: Optional[str]):
    MapEditor(map_file_name)


# TODO Convert these functions to methods

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
