import json

from pythongame.core.common import *
from pythongame.core.npc_creation import create_npc, set_global_path_finder
from pythongame.core.game_data import CONSUMABLES, ITEM_ENTITY_SIZE, ITEMS, WALLS
from pythongame.core.game_data import POTION_ENTITY_SIZE
from pythongame.core.game_state import WorldEntity, GameState, ConsumableOnGround, ItemOnGround, DecorationEntity, Wall
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.player_data import PLAYER_ENTITY_SIZE, INTIAL_PLAYER_STATE, PLAYER_ENTITY_SPEED

# TODO Avoid depending on pythongame.game_data from here

GRID_CELL_SIZE = 25


def create_game_state_from_json_file(camera_size: Tuple[int, int], map_file: str):
    with open(map_file) as map_file:
        json_data = json.loads(map_file.read())

        player_pos = json_data["player"]["position"]
        player_entity = WorldEntity(player_pos, PLAYER_ENTITY_SIZE, Sprite.PLAYER, Direction.RIGHT, PLAYER_ENTITY_SPEED)

        consumables = [_create_consumable_at_position(ConsumableType[p["consumable_type"]], p["position"]) for p in
                       json_data["consumables_on_ground"]]
        items = [_create_item_at_position(ItemType[i["item_type"]], i["position"]) for i in
                 json_data["items_on_ground"]]

        path_finder = GlobalPathFinder()
        set_global_path_finder(path_finder)
        enemies = [create_npc(NpcType[e["enemy_type"]], e["position"]) for e in json_data["enemies"]]

        walls = [_create_wall_at_position(WallType[w["wall_type"]], w["position"]) for w in json_data["walls"]]

        game_world_size = json_data["game_world_size"]

        decoration_entities = [DecorationEntity(d["position"], Sprite[d["sprite"]]) for d in json_data["decorations"]]
        game_state = GameState(player_entity, consumables, items, enemies, walls, camera_size, game_world_size,
                               INTIAL_PLAYER_STATE, decoration_entities)
        path_finder.set_grid(game_state.grid)
        return game_state


def save_game_state_to_json_file(game_state: GameState, map_file: str):
    json_data = {}

    json_data["enemies"] = []
    for e in game_state.non_player_characters:
        json_data["enemies"].append({"enemy_type": e.npc_type.name, "position": e.world_entity.get_position()})

    json_data["player"] = {"position": game_state.player_entity.get_position()}

    json_data["walls"] = []
    for w in game_state.walls:
        json_data["walls"].append({"wall_type": w.wall_type.name, "position": w.world_entity.get_position()})

    json_data["consumables_on_ground"] = []
    for p in game_state.consumables_on_ground:
        json_data["consumables_on_ground"].append(
            {"consumable_type": p.consumable_type.name, "position": p.world_entity.get_position()})

    json_data["items_on_ground"] = []
    for i in game_state.items_on_ground:
        json_data["items_on_ground"].append({"item_type": i.item_type.name, "position": i.world_entity.get_position()})

    json_data["decorations"] = []
    for d in game_state.decoration_entities:
        json_data["decorations"].append({"sprite": d.sprite.name, "position": d.get_position()})

    json_data["game_world_size"] = game_state.game_world_size

    with open(map_file, 'w') as map_file:
        map_file.write(json.dumps(json_data, indent=2))


def _create_consumable_at_position(consumable_type: ConsumableType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, POTION_ENTITY_SIZE, CONSUMABLES[consumable_type].entity_sprite)
    return ConsumableOnGround(entity, consumable_type)


def _create_item_at_position(item_type: ItemType, pos: Tuple[int, int]):
    entity = WorldEntity(pos, ITEM_ENTITY_SIZE, ITEMS[item_type].entity_sprite)
    return ItemOnGround(entity, item_type)


def _create_wall_at_position(wall_type: WallType, pos: Tuple[int, int]) -> Wall:
    return Wall(wall_type, WorldEntity(pos, WALLS[wall_type].size, WALLS[wall_type].sprite))
