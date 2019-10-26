import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer, ConsumableType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, register_npc_dialog_data, DialogData, \
    DialogOptionData, buy_consumable_option
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet


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


def register_warpstone_merchant_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_WARPSTONE_MERCHANT
    npc_type = NpcType.NEUTRAL_WARPSTONE_MERCHANT
    ui_icon_sprite = PortraitIconSprite.WARPSTONE_MERCHANT
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    introduction = "Hah! I managed to infuse the statues' teleporting powers into these stones. " \
                   "You can carry them with you and use them any time you want to return to this place!"
    dialog_options = [
        buy_consumable_option(ConsumableType.WARP_STONE, 2),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    dialog_data = DialogData(ui_icon_sprite, introduction, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/manga_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 0
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x, y), (x + 1, y), (x + 2, y)],
        Direction.LEFT: [(x, y + 1), (x + 1, y + 1), (x + 2, y + 1)],
        Direction.RIGHT: [(x, y + 2), (x + 1, y + 2), (x + 2, y + 2)],
        Direction.UP: [(x, y + 3), (x + 1, y + 3), (x + 2, y + 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(ui_icon_sprite, 'resources/graphics/portrait_warpstone_merchant_npc.png')
