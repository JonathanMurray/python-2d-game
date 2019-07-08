import sys
from pathlib import Path
from typing import Tuple, Optional, List, Dict

import pygame

from pythongame.core.common import Direction, Sprite, sum_of_vectors, WallType, NpcType, ConsumableType, ItemType
from pythongame.core.entity_creation import create_portal, create_player_world_entity, create_npc, create_wall, \
    create_consumable_on_ground, create_item_on_ground, create_decoration_entity, create_money_pile_on_ground
from pythongame.core.game_data import NON_PLAYER_CHARACTERS, CONSUMABLES, ITEMS, ITEM_ENTITY_SIZE, WALLS
from pythongame.core.game_data import POTION_ENTITY_SIZE
from pythongame.core.game_state import WorldEntity, GameState
from pythongame.core.view import View
from pythongame.game_data.player_data import get_initial_player_state
from pythongame.game_world_init import save_game_state_to_json_file, create_game_state_from_json_file
from pythongame.map_editor_world_entity import MapEditorWorldEntity
from pythongame.register_game_data import register_all_game_data

# TODO Avoid depending on pythongame.game_data from here


MAP_EDITOR_ENTITIES: List[MapEditorWorldEntity] = [
    MapEditorWorldEntity.player(),

    MapEditorWorldEntity.wall(WallType.WALL),
    MapEditorWorldEntity.wall(WallType.STATUE),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_N),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_NE),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_E),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_SE),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_S),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_SW),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_W),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_NW),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_POINTY_NE),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_POINTY_SE),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_POINTY_SW),
    MapEditorWorldEntity.wall(WallType.WALL_DIRECTIONAL_POINTY_NW),
    MapEditorWorldEntity.wall(WallType.WALL_CHAIR),
    MapEditorWorldEntity.wall(WallType.ALTAR),

    MapEditorWorldEntity.npc(NpcType.DARK_REAPER),
    MapEditorWorldEntity.npc(NpcType.RAT_1),
    MapEditorWorldEntity.npc(NpcType.RAT_2),
    MapEditorWorldEntity.npc(NpcType.GOBLIN_WARLOCK),
    MapEditorWorldEntity.npc(NpcType.MUMMY),
    MapEditorWorldEntity.npc(NpcType.NECROMANCER),
    MapEditorWorldEntity.npc(NpcType.WARRIOR),
    MapEditorWorldEntity.npc(NpcType.CHEST),

    MapEditorWorldEntity.portal(True),
    MapEditorWorldEntity.portal(False),

    MapEditorWorldEntity.npc(NpcType.NEUTRAL_DWARF),
    MapEditorWorldEntity.npc(NpcType.NEUTRAL_NOMAD),
    MapEditorWorldEntity.npc(NpcType.NEUTRAL_NINJA),

    MapEditorWorldEntity.consumable(ConsumableType.HEALTH_LESSER),
    MapEditorWorldEntity.consumable(ConsumableType.HEALTH),
    MapEditorWorldEntity.consumable(ConsumableType.MANA_LESSER),
    MapEditorWorldEntity.consumable(ConsumableType.MANA),
    MapEditorWorldEntity.consumable(ConsumableType.SCROLL_ABILITY_SUMMON),

    MapEditorWorldEntity.item(ItemType.WINGED_BOOTS),
    MapEditorWorldEntity.item(ItemType.SWORD_OF_LEECHING),
    MapEditorWorldEntity.item(ItemType.ROD_OF_LIGHTNING),
    MapEditorWorldEntity.item(ItemType.AMULET_OF_MANA_1),
    MapEditorWorldEntity.item(ItemType.SOLDIERS_HELMET_1),
    MapEditorWorldEntity.item(ItemType.BLESSED_SHIELD_1),
    MapEditorWorldEntity.item(ItemType.STAFF_OF_FIRE),
    MapEditorWorldEntity.item(ItemType.BLUE_ROBE_1),
    MapEditorWorldEntity.item(ItemType.ORB_OF_THE_MAGI_1),

    MapEditorWorldEntity.money(1),

    MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_PLANT)
]

MAP_EDITOR_INPUT_CHARS: List[str] = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'D', 'F',
    'G', 'H', 'J', 'K', 'L', 'C', 'V', 'B', 'N', 'M'
]

ENTITIES_BY_CHAR: Dict[str, MapEditorWorldEntity] = dict(zip(MAP_EDITOR_INPUT_CHARS, MAP_EDITOR_ENTITIES))

CHARS_BY_ENTITY: Dict[MapEditorWorldEntity, str] = {v: k for k, v in ENTITIES_BY_CHAR.items()}

SCREEN_SIZE = (1200, 750)
CAMERA_SIZE = (1200, 600)

register_all_game_data()

if 'S' in ENTITIES_BY_CHAR:
    raise Exception("'S' key should be reserved for saving, but it's claimed by entity: "
                    + str(ENTITIES_BY_CHAR['S']))


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


def main(args: List[str]):
    if len(args) == 1:
        map_file = args[0]
    else:
        map_file = "resources/maps/graphics_test.json"

    if Path(map_file).exists():
        game_state = create_game_state_from_json_file(CAMERA_SIZE, map_file)
    else:
        player_entity = create_player_world_entity((250, 250))
        player_state = get_initial_player_state()
        game_state = GameState(player_entity, [], [], [], [], [], CAMERA_SIZE, (500, 500), player_state, [], [])

    pygame.init()

    view = View(CAMERA_SIZE, SCREEN_SIZE)

    user_state = UserState.deleting_entities()

    is_mouse_button_down = False

    possible_grid_cell_sizes = [25, 50]
    grid_cell_size_index = 0
    grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]

    camera_move_distance = 100
    snapped_mouse_screen_position = (0, 0)
    snapped_mouse_world_position = (0, 0)
    exact_mouse_screen_position = (0, 0)
    is_snapped_mouse_within_world = True
    is_snapped_mouse_over_ui = False

    game_state.center_camera_on_player()
    game_state.camera_world_area.set_position(((game_state.camera_world_area.x // grid_cell_size) * grid_cell_size,
                                               (game_state.camera_world_area.y // grid_cell_size) * grid_cell_size))

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
                is_snapped_mouse_within_world = game_state.is_position_within_game_world(snapped_mouse_world_position)
                is_snapped_mouse_over_ui = view.is_screen_position_within_ui(snapped_mouse_screen_position)
                if is_mouse_button_down and is_snapped_mouse_within_world and not is_snapped_mouse_over_ui:
                    if user_state.placing_entity:
                        if user_state.placing_entity.wall_type:
                            _add_wall_to_position(game_state, snapped_mouse_world_position,
                                                  user_state.placing_entity.wall_type)
                        elif user_state.placing_entity.decoration:
                            _add_decoration_to_position(user_state.placing_entity.decoration_sprite, game_state,
                                                        snapped_mouse_world_position)
                    elif user_state.deleting_entities:
                        _delete_map_entities_from_position(game_state, snapped_mouse_world_position)
                    else:
                        _delete_map_decorations_from_position(game_state, snapped_mouse_world_position)

            if event.type == pygame.KEYDOWN:
                if event.unicode.upper() in ENTITIES_BY_CHAR:
                    user_state = UserState.placing_entity(ENTITIES_BY_CHAR[event.unicode.upper()])
                elif event.key == pygame.K_s:
                    save_file = map_file
                    save_game_state_to_json_file(game_state, save_file)
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
                    user_state = UserState.deleting_entities()
                elif event.key == pygame.K_z:
                    user_state = UserState.deleting_decorations()
                elif event.key == pygame.K_PLUS:
                    grid_cell_size_index = (grid_cell_size_index + 1) % len(possible_grid_cell_sizes)
                    grid_cell_size = possible_grid_cell_sizes[grid_cell_size_index]

            if event.type == pygame.MOUSEBUTTONDOWN:
                is_mouse_button_down = True
                if user_state.placing_entity:
                    entity_being_placed = user_state.placing_entity
                    if is_snapped_mouse_within_world and not is_snapped_mouse_over_ui:
                        if entity_being_placed.is_player:
                            game_state.player_entity.set_position(snapped_mouse_world_position)
                        elif entity_being_placed.npc_type:
                            npc = create_npc(entity_being_placed.npc_type, snapped_mouse_world_position)
                            game_state.add_non_player_character(npc)
                        elif entity_being_placed.wall_type:
                            _add_wall_to_position(game_state, snapped_mouse_world_position,
                                                  entity_being_placed.wall_type)
                        elif entity_being_placed.consumable_type:
                            consumable_on_ground = create_consumable_on_ground(
                                entity_being_placed.consumable_type, snapped_mouse_world_position)
                            game_state.consumables_on_ground.append(consumable_on_ground)
                        elif entity_being_placed.item_type:
                            item_on_ground = create_item_on_ground(
                                entity_being_placed.item_type, snapped_mouse_world_position)
                            game_state.items_on_ground.append(item_on_ground)
                        elif entity_being_placed.decoration_sprite:
                            _add_decoration_to_position(entity_being_placed.decoration_sprite, game_state,
                                                        snapped_mouse_world_position)
                        elif entity_being_placed.money_amount:
                            money_pile_on_ground = create_money_pile_on_ground(
                                entity_being_placed.money_amount, snapped_mouse_world_position)
                            game_state.money_piles_on_ground.append(money_pile_on_ground)
                        elif entity_being_placed.is_portal:
                            portal = create_portal(entity_being_placed.is_main_portal, snapped_mouse_world_position)
                            game_state.portals.append(portal)

                        else:
                            raise Exception("Unknown entity: " + str(entity_being_placed))
                elif user_state.deleting_entities:
                    _delete_map_entities_from_position(game_state, snapped_mouse_world_position)
                else:
                    _delete_map_decorations_from_position(game_state, snapped_mouse_world_position)

            if event.type == pygame.MOUSEBUTTONUP:
                is_mouse_button_down = False

        entities_to_render = game_state.get_all_entities_to_render()
        decorations_to_render = game_state.get_decorations_to_render()
        view.render_world(
            all_entities_to_render=entities_to_render,
            decorations_to_render=decorations_to_render,
            player_entity=game_state.player_entity,
            is_player_invisible=game_state.player_state.is_invisible,
            camera_world_area=game_state.camera_world_area,
            non_player_characters=game_state.non_player_characters,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=True,
            player_health=game_state.player_state.health,
            player_max_health=game_state.player_state.max_health,
            game_world_size=game_state.game_world_size,
            entity_action_text=None)

        entity_icon_hovered_by_mouse = view.render_map_editor_ui(
            chars_by_entities=CHARS_BY_ENTITY,
            entities=MAP_EDITOR_ENTITIES,
            placing_entity=user_state.placing_entity,
            deleting_entities=user_state.deleting_entities,
            deleting_decorations=user_state.deleting_decorations,
            num_enemies=len(game_state.non_player_characters),
            num_walls=len(game_state.walls),
            num_decorations=len(game_state.decoration_entities),
            grid_cell_size=grid_cell_size,
            mouse_screen_position=exact_mouse_screen_position)

        if is_mouse_button_down and entity_icon_hovered_by_mouse:
            user_state = UserState.placing_entity(entity_icon_hovered_by_mouse)

        if is_snapped_mouse_over_ui:
            pass
            # render nothing over UI
        elif not is_snapped_mouse_within_world:
            snapped_mouse_rect = (snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                  grid_cell_size, grid_cell_size)
            view.render_map_editor_mouse_rect((250, 50, 0), snapped_mouse_rect)
        elif user_state.placing_entity:
            entity_being_placed = user_state.placing_entity
            # TODO Extract common parts of this code. Store sprite in MapEditorWorldEntity?
            if entity_being_placed.npc_type:
                data = NON_PLAYER_CHARACTERS[entity_being_placed.npc_type]
                entity = WorldEntity((0, 0), data.size, data.sprite, Direction.DOWN, data.speed)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.is_player:
                view.render_map_editor_world_entity_at_position(game_state.player_entity, snapped_mouse_screen_position)
            elif entity_being_placed.wall_type:
                data = WALLS[entity_being_placed.wall_type]
                entity = WorldEntity((0, 0), data.size, data.sprite)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.consumable_type:
                sprite = CONSUMABLES[entity_being_placed.consumable_type].entity_sprite
                entity = WorldEntity((0, 0), POTION_ENTITY_SIZE, sprite)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.item_type:
                sprite = ITEMS[entity_being_placed.item_type].entity_sprite
                entity = WorldEntity((0, 0), ITEM_ENTITY_SIZE, sprite)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.decoration_sprite:
                entity = WorldEntity((0, 0), (0, 0), entity_being_placed.decoration_sprite)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.money_amount:
                entity = WorldEntity((0, 0), (0, 0), Sprite.COINS_5)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            elif entity_being_placed.is_portal:
                entity = WorldEntity((0, 0), (0, 0), Sprite.PORTAL)
                view.render_map_editor_world_entity_at_position(entity, snapped_mouse_screen_position)
            else:
                raise Exception("Unknown entity: " + str(entity_being_placed))
        elif user_state.deleting_entities:
            snapped_mouse_rect = (snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                  grid_cell_size, grid_cell_size)
            view.render_map_editor_mouse_rect((250, 250, 0), snapped_mouse_rect)
        elif user_state.deleting_decorations:
            snapped_mouse_rect = (snapped_mouse_screen_position[0], snapped_mouse_screen_position[1],
                                  grid_cell_size, grid_cell_size)
            view.render_map_editor_mouse_rect((0, 250, 250), snapped_mouse_rect)
        else:
            raise Exception("Unhandled user_state: " + str(user_state))

        view.update_display()


def _add_decoration_to_position(decoration_sprite: Sprite, game_state, snapped_mouse_world_position):
    already_has_decoration = any([d for d in game_state.decoration_entities
                                  if d.get_position() == snapped_mouse_world_position])
    if not already_has_decoration:
        decoration_entity = create_decoration_entity(snapped_mouse_world_position, decoration_sprite)
        game_state.decoration_entities.append(decoration_entity)


def _add_wall_to_position(game_state, snapped_mouse_world_position: Tuple[int, int], wall_type: WallType):
    already_has_wall = any([w for w in game_state.walls
                            if w.world_entity.get_position() == snapped_mouse_world_position])
    if not already_has_wall:
        wall = create_wall(wall_type, snapped_mouse_world_position)
        game_state.add_wall(wall)


def _delete_map_entities_from_position(game_state: GameState, snapped_mouse_world_position: Tuple[int, int]):
    for wall in [w for w in game_state.walls if w.world_entity.get_position() == snapped_mouse_world_position]:
        game_state.remove_wall(wall)
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


def _delete_map_decorations_from_position(game_state, snapped_mouse_world_position: Tuple[int, int]):
    for d in [d for d in game_state.decoration_entities if (d.x, d.y) == snapped_mouse_world_position]:
        game_state.decoration_entities.remove(d)
