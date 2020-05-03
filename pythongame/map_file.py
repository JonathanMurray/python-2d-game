import json

from pygame.rect import Rect

from pythongame.core.common import *
from pythongame.core.entity_creation import create_npc, create_money_pile_on_ground, \
    create_consumable_on_ground, create_portal, create_wall, create_decoration_entity, create_item_on_ground, \
    create_chest, create_shrine, \
    create_dungeon_entrance
from pythongame.core.game_state import NonPlayerCharacter, Wall, Portal, DecorationEntity, \
    MoneyPileOnGround, ItemOnGround, ConsumableOnGround, Chest, Shrine, DungeonEntrance, GameWorldState
from pythongame.core.world_entity import WorldEntity


class MapEditorConfig:
    def __init__(self, disable_smart_grid: bool):
        self.disable_smart_grid = disable_smart_grid


class MapData:
    def __init__(self,
                 game_world: GameWorldState,
                 map_editor_config: MapEditorConfig,
                 grid_string: str,
                 player_position: Tuple[int, int]):
        self.game_world = game_world
        self.map_editor_config = map_editor_config
        self.grid_string = grid_string
        self.player_position = player_position


def load_map_from_json_file(map_file_path: str) -> MapData:
    with open(map_file_path) as map_file:
        json_data = json.loads(map_file.read())
        return create_map_from_json(json_data)


def create_map_from_json(json_data) -> MapData:
    return MapJson.deserialize(json_data)


def save_map_to_json_file(map_data: MapData, map_file: str):
    json_data = MapJson.serialize(map_data)
    write_json_to_file(json_data, map_file)


def write_json_to_file(json_data, map_file: str):
    with open(map_file, 'w') as map_file:
        map_file.write(json.dumps(json_data, indent=2))


class MapJson:

    @staticmethod
    def serialize(map_data: MapData):
        game_world = map_data.game_world
        config = map_data.map_editor_config
        grid = map_data.grid_string
        return {
            "grid": grid,
            "disable_smart_grid": config.disable_smart_grid,
            "player": PlayerJson.serialize(game_world.player_entity),
            "consumables_on_ground": [ConsumableJson.serialize(p) for p in game_world.consumables_on_ground],
            "items_on_ground": [ItemJson.serialize(i) for i in game_world.items_on_ground],
            "money_piles_on_ground": [MoneyJson.serialize(m) for m in game_world.money_piles_on_ground],
            "non_player_characters": [NpcJson.serialize(npc) for npc in game_world.non_player_characters],
            "walls": [WallJson.serialize(wall) for wall in game_world.walls_state.walls],
            "entire_world_area": WorldAreaJson.serialize(game_world.entire_world_area),
            "decorations": [DecorationJson.serialize(d) for d in
                            game_world.decorations_state.decoration_entities],
            "portals": [PortalJson.serialize(p) for p in game_world.portals],
            "chests": [ChestJson.serialize(c) for c in game_world.chests],
            "shrines": [ShrineJson.serialize(s) for s in game_world.shrines],
            "dungeon_entrances": [DungeonEntranceJson.serialize(e) for e in game_world.dungeon_entrances]
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
            "chests": [],
            "shrines": [],
            "dungeon_entrances": []
        }

    @staticmethod
    def deserialize(data) -> MapData:
        game_world = GameWorldState(
            non_player_characters=[NpcJson.deserialize(e) for e in
                                   data.get("non_player_characters", [])],
            walls=[WallJson.deserialize(w) for w in data.get("walls", [])],
            entire_world_area=WorldAreaJson.deserialize(data["entire_world_area"]),
            decoration_entities=[DecorationJson.deserialize(d) for d in data.get("decorations", [])],
            portals=[PortalJson.deserialize(p) for p in data.get("portals", [])],
            chests=[ChestJson.deserialize(c) for c in data.get("chests", [])],
            shrines=[ShrineJson.deserialize(s) for s in data.get("shrines", [])],
            dungeon_entrances=[DungeonEntranceJson.deserialize(e) for e in
                               data.get("dungeon_entrances", [])],
            consumables_on_ground=[ConsumableJson.deserialize(p) for p in
                                   data.get("consumables_on_ground", [])],
            items_on_ground=[ItemJson.deserialize(i) for i in data.get("items_on_ground", [])],
            money_piles_on_ground=[MoneyJson.deserialize(p) for p in
                                   data.get("money_piles_on_ground", [])],
            player_entity=None,
        )

        map_editor_config = MapEditorConfig(disable_smart_grid=data.get("disable_smart_grid", False))
        grid_string = data.get("grid", None)
        player_position = PlayerJson.deserialize(data["player"])
        return MapData(game_world, map_editor_config, grid_string, player_position)


class PlayerJson:
    @staticmethod
    def serialize(entity: WorldEntity):
        return PlayerJson.serialize_from_position(entity.get_position())

    @staticmethod
    def serialize_from_position(position: Tuple[int, int]):
        return {"position": position}

    @staticmethod
    def deserialize(data) -> Tuple[int, int]:
        return data["position"]


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


class ShrineJson:
    @staticmethod
    def serialize(shrine: Shrine):
        return {"position": shrine.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> Shrine:
        return create_shrine(data["position"])


class DungeonEntranceJson:
    @staticmethod
    def serialize(dungeon_entrance: DungeonEntrance):
        return {"position": dungeon_entrance.world_entity.get_position()}

    @staticmethod
    def deserialize(data) -> DungeonEntrance:
        return create_dungeon_entrance(data["position"])


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
        return ItemJson.serialize_from_data(item.item_id, item.world_entity.get_position())

    @staticmethod
    def serialize_from_data(item_id: ItemId, position: Tuple[int, int]):
        return {"item_id": item_id.stats_string, "position": position, "item_name": item_id.name}

    @staticmethod
    def deserialize(data) -> ItemOnGround:
        item_id = ItemId.from_stats_string(data["item_id"], data["item_name"])
        return create_item_on_ground(item_id, data["position"])


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
