import json
from typing import Tuple

from pygame.rect import Rect

from pythongame.core.common import *
from pythongame.core.entity_creation import create_npc, set_global_path_finder, create_money_pile_on_ground, \
    create_consumable_on_ground, create_portal, create_wall, create_hero_world_entity, \
    create_decoration_entity, create_item_on_ground, create_player_state, create_chest
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter, Wall, Portal, DecorationEntity, \
    MoneyPileOnGround, ItemOnGround, ConsumableOnGround, PlayerState, Chest
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder


def create_game_state_from_json_file(camera_size: Tuple[int, int], map_file_path: str, hero_id: HeroId) -> GameState:
    with open(map_file_path) as map_file:
        json_data = json.loads(map_file.read())
        return create_game_state_from_map_data(camera_size, json_data, hero_id)


def create_game_state_from_map_data(camera_size: Tuple[int, int], json_data, hero_id: HeroId) -> GameState:
    path_finder = GlobalPathFinder()
    set_global_path_finder(path_finder)

    player_state = create_player_state(hero_id)
    game_state = MapJson.deserialize(json_data, player_state, camera_size)

    path_finder.set_grid(game_state.pathfinder_wall_grid)
    return game_state


def save_game_state_to_json_file(game_state: GameState, map_file: str):
    json_data = MapJson.serialize(game_state)
    save_map_data_to_file(json_data, map_file)


def save_map_data_to_file(json_data, map_file: str):
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
            "non_player_characters": [NpcJson.serialize(npc) for npc in game_state.non_player_characters],
            "walls": [WallJson.serialize(wall) for wall in game_state.walls_state.walls],
            "entire_world_area": WorldAreaJson.serialize(game_state.entire_world_area),
            "decorations": [DecorationJson.serialize(d) for d in game_state.decorations_state.decoration_entities],
            "portals": [PortalJson.serialize(p) for p in game_state.portals],
            "chests": [ChestJson.serialize(c) for c in game_state.chests]
        }

    @staticmethod
    def serialize_from_data(walls: List[Wall], decorations: List[DecorationEntity],
                            items_on_ground: List[ItemOnGround], entire_world_area: Rect,
                            player_position: Tuple[int, int], npcs: List[NonPlayerCharacter]):
        return {
            "player": PlayerJson.serialize_from_position(player_position),
            "consumables_on_ground": [],
            "items_on_ground": [ItemJson.serialize(i) for i in items_on_ground],
            "money_piles_on_ground": [],
            "non_player_characters": [NpcJson.serialize(npc) for npc in npcs],
            "walls": [WallJson.serialize(wall) for wall in walls],
            "entire_world_area": WorldAreaJson.serialize(entire_world_area),
            "decorations": [DecorationJson.serialize(decoration_entity) for decoration_entity in decorations],
            "portals": [],
            "chests": []
        }

    @staticmethod
    def deserialize(data, player_state: PlayerState, camera_size: Tuple[int, int]) -> GameState:
        return GameState(
            player_entity=PlayerJson.deserialize(player_state.hero_id, data["player"]),
            consumables_on_ground=[ConsumableJson.deserialize(p) for p in data.get("consumables_on_ground", [])],
            items_on_ground=[ItemJson.deserialize(i) for i in data.get("items_on_ground", [])],
            money_piles_on_ground=[MoneyJson.deserialize(p) for p in data.get("money_piles_on_ground", [])],
            non_player_characters=[NpcJson.deserialize(e) for e in data.get("non_player_characters", [])],
            walls=[WallJson.deserialize(w) for w in data.get("walls", [])],
            camera_size=camera_size,
            entire_world_area=WorldAreaJson.deserialize(data["entire_world_area"]),
            player_state=player_state,
            decoration_entities=[DecorationJson.deserialize(d) for d in data.get("decorations", [])],
            portals=[PortalJson.deserialize(p) for p in data.get("portals", [])],
            chests=[ChestJson.deserialize(c) for c in data.get("chests", [])]
        )


class PlayerJson:
    @staticmethod
    def serialize(entity: WorldEntity):
        return PlayerJson.serialize_from_position(entity.get_position())

    @staticmethod
    def serialize_from_position(position: Tuple[int, int]):
        return {"position": position}

    @staticmethod
    def deserialize(hero_id: HeroId, data) -> WorldEntity:
        return create_hero_world_entity(hero_id, data["position"])


class NpcJson:
    @staticmethod
    def serialize(enemy: NonPlayerCharacter):
        return {"npc_type": enemy.npc_type.name, "position": enemy.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> NonPlayerCharacter:
        return create_npc(NpcType[data["npc_type"]], data["position"])


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


class ChestJson:
    @staticmethod
    def serialize(chest: Chest):
        return {"position": chest.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> Chest:
        return create_chest(data["position"])


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
        return ItemJson.serialize_from_data(item.item_type, item.world_entity.get_position())

    @staticmethod
    def serialize_from_data(item_type: ItemType, position: Tuple[int, int]):
        return {"item_type": item_type.name, "position": position}

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


class WorldAreaJson:
    @staticmethod
    def serialize(game_world_area: Rect):
        return [game_world_area.x, game_world_area.y, game_world_area.w, game_world_area.h]

    @staticmethod
    def deserialize(data) -> Rect:
        return Rect(data[0], data[1], data[2], data[3])
