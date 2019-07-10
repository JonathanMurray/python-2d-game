import json
from typing import Tuple

from pythongame.core.common import *
from pythongame.core.entity_creation import create_npc, set_global_path_finder, create_money_pile_on_ground, \
    create_consumable_on_ground, create_portal, create_wall, create_player_world_entity, \
    create_decoration_entity, create_item_on_ground
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Wall, Portal, DecorationEntity, \
    MoneyPileOnGround, ItemOnGround, ConsumableOnGround, PlayerState
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.game_data.player_data import get_initial_player_state


# TODO Avoid depending on pythongame.game_data from here


def create_game_state_from_json_file(camera_size: Tuple[int, int], map_file: str):
    with open(map_file) as map_file:
        json_data = json.loads(map_file.read())

        path_finder = GlobalPathFinder()
        set_global_path_finder(path_finder)

        player_state = get_initial_player_state()
        game_state = MapJson.deserialize(json_data, player_state, camera_size)

        path_finder.set_grid(game_state.grid)
        return game_state


def save_game_state_to_json_file(game_state: GameState, map_file: str):
    json_data = MapJson.serialize(game_state)
    with open(map_file, 'w') as map_file:
        map_file.write(json.dumps(json_data, indent=2))


class MapJson:
    @staticmethod
    def serialize(game_state: GameState):
        return {
            "player": PlayerJson.serialize(game_state.player_entity),
            "consumables_on_ground": [ConsumableJson.serialize(p) for p in game_state.consumables_on_ground],
            "items_on_ground": [ItemJson.serialize(i) for i in game_state.items_on_ground],
            "money_piles_on_ground": [MoneyJson.serialize(m) for m in game_state.money_piles_on_ground],
            "enemies": [EnemyJson.serialize(npc) for npc in game_state.non_player_characters],
            "walls": [WallJson.serialize(wall) for wall in game_state.walls],
            "game_world_size": game_state.game_world_size,
            "decorations": [DecorationJson.serialize(d) for d in game_state.decoration_entities],
            "portals": [PortalJson.serialize(p) for p in game_state.portals]
        }

    @staticmethod
    def deserialize(data, player_state: PlayerState, camera_size: Tuple[int, int]) -> GameState:
        return GameState(
            player_entity=(PlayerJson.deserialize(data["player"])),
            consumables_on_ground=[ConsumableJson.deserialize(p) for p in data.get("consumables_on_ground", [])],
            items_on_ground=[ItemJson.deserialize(i) for i in data.get("items_on_ground", [])],
            money_piles_on_ground=[MoneyJson.deserialize(p) for p in data.get("money_piles_on_ground", [])],
            non_player_characters=[EnemyJson.deserialize(e) for e in data.get("enemies", [])],
            walls=[WallJson.deserialize(w) for w in data.get("walls", [])],
            camera_size=camera_size,
            game_world_size=(data["game_world_size"]),
            player_state=player_state,
            decoration_entities=[DecorationJson.deserialize(d) for d in data.get("decorations", [])],
            portals=[PortalJson.deserialize(p) for p in data.get("portals", [])]
        )


class PlayerJson:
    @staticmethod
    def serialize(entity: WorldEntity):
        return {"position": entity.get_position()}

    @staticmethod
    def deserialize(data) -> WorldEntity:
        return create_player_world_entity(data["position"])


# TODO This is more than enemies!
class EnemyJson:
    @staticmethod
    def serialize(enemy: NonPlayerCharacter):
        return {"enemy_type": enemy.npc_type.name, "position": enemy.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> NonPlayerCharacter:
        return create_npc(NpcType[data["enemy_type"]], data["position"])


class WallJson:
    @staticmethod
    def serialize(wall: Wall):
        return {"wall_type": wall.wall_type.name, "position": wall.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> Wall:
        return create_wall(WallType[data["wall_type"]], data["position"])


class PortalJson:
    @staticmethod
    def serialize(portal: Portal):
        return {"portal_id": portal.portal_id.name, "position": portal.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> Portal:
        return create_portal(PortalId[data["portal_id"]], data["position"])


class DecorationJson:
    @staticmethod
    def serialize(decoration: DecorationEntity):
        return {"sprite": decoration.sprite.name, "position": decoration.get_position()}

    @staticmethod
    def deserialize(data) -> DecorationEntity:
        return create_decoration_entity(data["position"], Sprite[data["sprite"]])


class MoneyJson:
    @staticmethod
    def serialize(money: MoneyPileOnGround):
        return {"amount": money.amount, "position": money.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> MoneyPileOnGround:
        return create_money_pile_on_ground(data["amount"], data["position"])


class ItemJson:
    @staticmethod
    def serialize(item: ItemOnGround):
        return {"item_type": item.item_type.name, "position": item.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> ItemOnGround:
        return create_item_on_ground(ItemType[data["item_type"]], data["position"])


class ConsumableJson:
    @staticmethod
    def serialize(consumable: ConsumableOnGround):
        return {"consumable_type": consumable.consumable_type.name, "position": consumable.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> ConsumableOnGround:
        return create_consumable_on_ground(ConsumableType[data["consumable_type"]], data["position"])
