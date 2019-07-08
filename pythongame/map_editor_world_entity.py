from typing import Optional

from pythongame.core.common import Sprite, WallType, NpcType, ConsumableType, ItemType


class MapEditorWorldEntity:
    def __init__(self):
        self.npc_type: NpcType = None
        self.is_player: bool = False
        self.wall_type: Optional[WallType] = None
        self.consumable_type: Optional[ConsumableType] = None
        self.item_type: Optional[ItemType] = None
        self.decoration_sprite: Optional[Sprite] = None
        self.money_amount: Optional[int] = None
        self.is_portal = False
        self.is_main_portal = False

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        # No need for efficiency in this class
        return 0

    @staticmethod
    def player():
        e = MapEditorWorldEntity()
        e.is_player = True
        return e

    @staticmethod
    def npc(npc_type: NpcType):
        e = MapEditorWorldEntity()
        e.npc_type = npc_type
        return e

    @staticmethod
    def wall(wall_type: WallType):
        e = MapEditorWorldEntity()
        e.wall_type = wall_type
        return e

    @staticmethod
    def consumable(consumable_type: ConsumableType):
        e = MapEditorWorldEntity()
        e.consumable_type = consumable_type
        return e

    @staticmethod
    def item(item_type: ItemType):
        e = MapEditorWorldEntity()
        e.item_type = item_type
        return e

    @staticmethod
    def decoration(sprite: Sprite):
        e = MapEditorWorldEntity()
        e.decoration_sprite = sprite
        return e

    @staticmethod
    def money(amount: int):
        e = MapEditorWorldEntity()
        e.money_amount = amount
        return e

    @staticmethod
    def portal(is_main_portal: bool):
        e = MapEditorWorldEntity()
        e.is_portal = True
        e.is_main_portal = is_main_portal
        return e

# TODO Move large chunks of branching code from map_editor in here
