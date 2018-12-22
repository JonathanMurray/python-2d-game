from typing import Optional

from pythongame.core.common import Sprite, WallType, EnemyType, PotionType, ItemType


class MapEditorWorldEntity:
    def __init__(self, enemy_type: Optional[EnemyType], is_player: bool, wall_type: Optional[WallType],
                 potion_type: Optional[PotionType], item_type: Optional[ItemType], decoration_sprite: Optional[Sprite]):
        self.enemy_type = enemy_type
        self.is_player = is_player
        self.wall_type = wall_type
        self.potion_type = potion_type
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
    def enemy(enemy_type: EnemyType):
        return MapEditorWorldEntity(enemy_type, False, None, None, None, None)

    @staticmethod
    def wall(wall_type: WallType):
        return MapEditorWorldEntity(None, False, wall_type, None, None, None)

    @staticmethod
    def potion(potion_type: PotionType):
        return MapEditorWorldEntity(None, False, None, potion_type, None, None)

    @staticmethod
    def item(item_type: ItemType):
        return MapEditorWorldEntity(None, False, None, None, item_type, None)

    @staticmethod
    def decoration(sprite: Sprite):
        return MapEditorWorldEntity(None, False, None, None, None, sprite)
