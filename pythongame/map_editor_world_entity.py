from typing import Optional

from pythongame.core.common import Sprite, WallType, NpcType, ConsumableType, ItemType


class MapEditorWorldEntity:
    def __init__(self, npc_type: Optional[NpcType], is_player: bool, wall_type: Optional[WallType],
                 consumable_type: Optional[ConsumableType], item_type: Optional[ItemType], decoration_sprite: Optional[Sprite]):
        self.npc_type = npc_type
        self.is_player = is_player
        self.wall_type = wall_type
        self.consumable_type = consumable_type
        self.item_type = item_type
        self.decoration_sprite = decoration_sprite

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __hash__(self):
        # No need for efficiency in this class
        return 0

    @staticmethod
    def player():
        return MapEditorWorldEntity(None, True, None, None, None, None)

    @staticmethod
    def enemy(npc_type: NpcType):
        return MapEditorWorldEntity(npc_type, False, None, None, None, None)

    @staticmethod
    def wall(wall_type: WallType):
        return MapEditorWorldEntity(None, False, wall_type, None, None, None)

    @staticmethod
    def consumable(consumable_type: ConsumableType):
        return MapEditorWorldEntity(None, False, None, consumable_type, None, None)

    @staticmethod
    def item(item_type: ItemType):
        return MapEditorWorldEntity(None, False, None, None, item_type, None)

    @staticmethod
    def decoration(sprite: Sprite):
        return MapEditorWorldEntity(None, False, None, None, None, sprite)
