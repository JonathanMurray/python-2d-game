import sys
from pathlib import Path
from typing import Tuple, Optional, List, Dict

import pygame

from pythongame.core.common import Sprite, WallType, NpcType, ConsumableType, ItemType, PortalId, HeroId
from pythongame.core.entity_creation import create_portal, create_hero_world_entity, create_npc, create_wall, \
    create_consumable_on_ground, create_item_on_ground, create_decoration_entity, create_money_pile_on_ground, \
    create_player_state
from pythongame.core.game_state import GameState, WorldArea
from pythongame.core.math import sum_of_vectors
from pythongame.core.view import View
from pythongame.game_world_init import save_game_state_to_json_file, create_game_state_from_json_file
from pythongame.map_editor_world_entity import MapEditorWorldEntity
from pythongame.register_game_data import register_all_game_data

MAP_DIR = "resources/maps/"

register_all_game_data()

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

    MapEditorWorldEntity.npc(NpcType.GOBLIN_WORKER),
    MapEditorWorldEntity.npc(NpcType.GOBLIN_SPEARMAN),
    MapEditorWorldEntity.npc(NpcType.GOBLIN_SPEARMAN_ELITE),
    MapEditorWorldEntity.npc(NpcType.GOBLIN_WARRIOR),
    MapEditorWorldEntity.npc(NpcType.DARK_REAPER),
    MapEditorWorldEntity.npc(NpcType.RAT_1),
    MapEditorWorldEntity.npc(NpcType.RAT_2),
    MapEditorWorldEntity.npc(NpcType.GOBLIN_WARLOCK),
    MapEditorWorldEntity.npc(NpcType.MUMMY),
    MapEditorWorldEntity.npc(NpcType.NECROMANCER),
    MapEditorWorldEntity.npc(NpcType.WARRIOR),
    MapEditorWorldEntity.npc(NpcType.CHEST),

    MapEditorWorldEntity.portal(PortalId.A_BASE),
    MapEditorWorldEntity.portal(PortalId.B_BASE),
    MapEditorWorldEntity.portal(PortalId.C_BASE),
    MapEditorWorldEntity.portal(PortalId.A_REMOTE),
    MapEditorWorldEntity.portal(PortalId.B_REMOTE),
    MapEditorWorldEntity.portal(PortalId.C_REMOTE),

    MapEditorWorldEntity.npc(NpcType.NEUTRAL_DWARF),
    MapEditorWorldEntity.npc(NpcType.NEUTRAL_NOMAD),
    MapEditorWorldEntity.npc(NpcType.NEUTRAL_NINJA),

    MapEditorWorldEntity.consumable(ConsumableType.HEALTH_LESSER),
    MapEditorWorldEntity.consumable(ConsumableType.HEALTH),
    MapEditorWorldEntity.consumable(ConsumableType.MANA_LESSER),
    MapEditorWorldEntity.consumable(ConsumableType.MANA),
    MapEditorWorldEntity.consumable(ConsumableType.SCROLL_SUMMON_DRAGON),
    MapEditorWorldEntity.consumable(ConsumableType.INVISIBILITY),
    MapEditorWorldEntity.consumable(ConsumableType.SPEED),
    MapEditorWorldEntity.consumable(ConsumableType.BREW),

    MapEditorWorldEntity.item(ItemType.MESSENGERS_HAT),
    MapEditorWorldEntity.item(ItemType.SWORD_OF_LEECHING),
    MapEditorWorldEntity.item(ItemType.ROD_OF_LIGHTNING),
    MapEditorWorldEntity.item(ItemType.AMULET_OF_MANA_1),
    MapEditorWorldEntity.item(ItemType.SOLDIERS_HELMET_1),
    MapEditorWorldEntity.item(ItemType.BLESSED_SHIELD_1),
    MapEditorWorldEntity.item(ItemType.STAFF_OF_FIRE),
    MapEditorWorldEntity.item(ItemType.BLUE_ROBE_1),
    MapEditorWorldEntity.item(ItemType.ORB_OF_THE_MAGI_1),
    MapEditorWorldEntity.item(ItemType.WIZARDS_COWL),
    MapEditorWorldEntity.item(ItemType.ZULS_AEGIS),
    MapEditorWorldEntity.item(ItemType.KNIGHTS_ARMOR),
    MapEditorWorldEntity.item(ItemType.GOATS_RING),
    MapEditorWorldEntity.item(ItemType.WOODEN_SHIELD),
    MapEditorWorldEntity.item(ItemType.ELVEN_ARMOR),
    MapEditorWorldEntity.item(ItemType.GOLD_NUGGET),
    MapEditorWorldEntity.item(ItemType.SAPHIRE),
    MapEditorWorldEntity.item(ItemType.BLOOD_AMULET),
    MapEditorWorldEntity.item(ItemType.LEATHER_COWL),
    MapEditorWorldEntity.item(ItemType.WINGED_HELMET),
    MapEditorWorldEntity.item(ItemType.ELITE_ARMOR),
    MapEditorWorldEntity.item(ItemType.RING_OF_POWER),


    MapEditorWorldEntity.money(1),

    MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_GROUND_STONE_GRAY),
    MapEditorWorldEntity.decoration(Sprite.DECORATION_PLANT),
    MapEditorWorldEntity.wall(WallType.SHELF_EMPTY),
    MapEditorWorldEntity.wall(WallType.SHELF_HELMETS),
    MapEditorWorldEntity.wall(WallType.SHELF_ARMORS),
    MapEditorWorldEntity.wall(WallType.BARREL_1),
    MapEditorWorldEntity.wall(WallType.BARREL_2),
    MapEditorWorldEntity.wall(WallType.BARREL_3),
    MapEditorWorldEntity.wall(WallType.BARREL_4),
    MapEditorWorldEntity.wall(WallType.BARREL_5),
    MapEditorWorldEntity.wall(WallType.BARREL_6),
]

MAP_EDITOR_INPUT_CHARS: List[str] = [
    '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', 'A', 'D', 'F',
    'G', 'H', 'J', 'K', 'L', 'C', 'V', 'B', 'N', 'M'
]

ENTITIES_BY_CHAR: Dict[str, MapEditorWorldEntity] = dict(zip(MAP_EDITOR_INPUT_CHARS, MAP_EDITOR_ENTITIES))

CHARS_BY_ENTITY: Dict[MapEditorWorldEntity, str] = {v: k for k, v in ENTITIES_BY_CHAR.items()}

SCREEN_SIZE = (1200, 750)
CAMERA_SIZE = (1200, 550)

# The choice of hero shouldn't matter in the map editor, as we only store its position in the map file
HERO_ID = HeroId.MAGE

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


def main(map_file_name: Optional[str]):
    map_file_path = MAP_DIR + (map_file_name or "map1.json")

    if Path(map_file_path).exists():
        game_state = create_game_state_from_json_file(CAMERA_SIZE, map_file_path, HERO_ID)
    else:

        player_entity = create_hero_world_entity(HERO_ID, (0, 0))
        player_state = create_player_state(HERO_ID)
        game_state = GameState(player_entity, [], [], [], [], [], CAMERA_SIZE, WorldArea((-250, -250), (500, 500)),
                               player_state, [], [])

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
                            _add_wall(game_state, snapped_mouse_world_position, user_state.placing_entity.wall_type)
                        elif user_state.placing_entity.decoration_sprite:
                            _add_decoration(user_state.placing_entity.decoration_sprite, game_state,
                                            snapped_mouse_world_position)
                    elif user_state.deleting_entities:
                        _delete_map_entities_from_position(game_state, snapped_mouse_world_position)
                    else:
                        _delete_map_decorations_from_position(game_state, snapped_mouse_world_position)

            if event.type == pygame.KEYDOWN:
                if event.unicode.upper() in ENTITIES_BY_CHAR:
                    user_state = UserState.placing_entity(ENTITIES_BY_CHAR[event.unicode.upper()])
                elif event.key == pygame.K_s:
                    save_file = map_file_path
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
            player_active_buffs=game_state.player_state.active_buffs,
            camera_world_area=game_state.camera_world_area,
            non_player_characters=game_state.non_player_characters,
            visual_effects=game_state.visual_effects,
            render_hit_and_collision_boxes=True,
            player_health=game_state.player_state.health_resource.value,
            player_max_health=game_state.player_state.health_resource.max_value,
            entire_world_area=game_state.entire_world_area,
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
            view.render_map_editor_world_entity_at_position(
                entity_being_placed.sprite, entity_being_placed.entity_size, snapped_mouse_screen_position)
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


def _add_decoration(decoration_sprite: Sprite, game_state, snapped_mouse_world_position):
    already_has_decoration = any([d for d in game_state.decoration_entities
                                  if d.get_position() == snapped_mouse_world_position])
    if not already_has_decoration:
        decoration_entity = create_decoration_entity(snapped_mouse_world_position, decoration_sprite)
        game_state.decoration_entities.append(decoration_entity)


def _add_wall(game_state, snapped_mouse_world_position: Tuple[int, int], wall_type: WallType):
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
