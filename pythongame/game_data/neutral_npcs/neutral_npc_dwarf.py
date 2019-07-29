import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite, ItemType, PeriodicTimer
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    register_npc_dialog_data, DialogData, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder

ITEM_TYPE_GOLD = ItemType.GOLD_NUGGET


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self.timer = PeriodicTimer(Millis(500))

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


class BuyTreasure(AbstractNpcAction):

    def __init__(self, item_type: ItemType, price: int, name: str):
        self.item_type = item_type
        self.price = price
        self.name = name

    def act(self, game_state: GameState) -> Optional[str]:
        player_has_it = game_state.player_state.item_inventory.has_item_in_inventory(self.item_type)
        if player_has_it:
            game_state.player_state.item_inventory.lose_item_from_inventory(self.item_type)
            game_state.player_state.money += self.price
            return "Sold " + self.name
        else:
            return "You don't have that!"


def register_dwarf_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_DWARF
    npc_type = NpcType.NEUTRAL_DWARF
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    introdution = "Hello there. I'm always looking for treasure. If you find any, we might be able to strike a deal!"
    dialog_options = [
        DialogOptionData("Gold nugget [20 gold]", "sell", BuyTreasure(ItemType.GOLD_NUGGET, 20, "gold nugget"),
                         UiIconSprite.ITEM_GOLD_NUGGET),
        DialogOptionData("Saphire [30 gold]", "sell", BuyTreasure(ItemType.SAPHIRE, 30, "saphire"),
                         UiIconSprite.ITEM_SAPHIRE),
        DialogOptionData("\"Good bye\"", "cancel", None, UiIconSprite.MAP_EDITOR_TRASHCAN)]
    dialog_data = DialogData(PortraitIconSprite.VIKING, introdution, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(0, 4), (1, 4), (2, 4)],
        Direction.LEFT: [(0, 5), (1, 5), (2, 5)],
        Direction.RIGHT: [(0, 6), (1, 6), (2, 6)],
        Direction.UP: [(0, 7), (1, 7), (2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(PortraitIconSprite.VIKING, 'resources/graphics/viking_portrait.png')
