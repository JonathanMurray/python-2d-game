import json

from pythongame.core.common import *
from pythongame.core.entity_creation import create_npc, set_global_path_finder, create_money_pile_on_ground, \
    create_item_on_ground, create_consumable_on_ground, create_portal, create_wall, create_player_world_entity
from pythongame.core.game_state import GameState, DecorationEntity
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.player_data import get_initial_player_state

# TODO Avoid depending on pythongame.game_data from here

GRID_CELL_SIZE = 25


# TODO Clean up JSON handling. Add classes that take care of (de-)serializing a specific object?


def create_game_state_from_json_file(camera_size: Tuple[int, int], map_file: str):
    with open(map_file) as map_file:
        json_data = json.loads(map_file.read())

        player_pos = json_data["player"]["position"]
        player_entity = create_player_world_entity(player_pos)

        consumables = [create_consumable_on_ground(ConsumableType[p["consumable_type"]], p["position"]) for p in
                       json_data["consumables_on_ground"]]
        items = [create_item_on_ground(ItemType[i["item_type"]], i["position"]) for i in
                 json_data["items_on_ground"]]

        json_money_piles_on_ground = json_data.get("money_piles_on_ground", [])
        money_piles = [create_money_pile_on_ground(p["amount"], p["position"]) for p in json_money_piles_on_ground]

        path_finder = GlobalPathFinder()
        set_global_path_finder(path_finder)
        enemies = [create_npc(NpcType[e["enemy_type"]], e["position"]) for e in json_data["enemies"]]

        walls = [create_wall(WallType[w["wall_type"]], w["position"]) for w in json_data["walls"]]

        game_world_size = json_data["game_world_size"]

        decoration_entities = [DecorationEntity(d["position"], Sprite[d["sprite"]]) for d in json_data["decorations"]]
        portals = [create_portal(p["is_main_portal"], p["position"]) for p in json_data["portals"]]
        player_state = get_initial_player_state()
        game_state = GameState(player_entity, consumables, items, money_piles, enemies, walls, camera_size,
                               game_world_size, player_state, decoration_entities, portals)

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

    json_data["money_piles_on_ground"] = []
    for m in game_state.money_piles_on_ground:
        json_data["money_piles_on_ground"].append({"amount": m.amount, "position": m.world_entity.get_position()})

    json_data["decorations"] = []
    for d in game_state.decoration_entities:
        json_data["decorations"].append({"sprite": d.sprite.name, "position": d.get_position()})

    json_data["portals"] = []
    for p in game_state.portals:
        json_data["portals"].append({"is_main_portal": p.is_main_portal, "position": p.world_entity.get_position()})

    json_data["game_world_size"] = game_state.game_world_size

    with open(map_file, 'w') as map_file:
        map_file.write(json.dumps(json_data, indent=2))
