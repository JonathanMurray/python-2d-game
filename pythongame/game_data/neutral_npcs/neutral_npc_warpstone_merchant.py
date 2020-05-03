import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer, ConsumableType
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, DialogData, \
    DialogOptionData, buy_consumable_option, register_conditional_npc_dialog_data
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.world_entity import WorldEntity

NPC_TYPE = NpcType.NEUTRAL_WARPSTONE_MERCHANT
UI_ICON_SPRITE = PortraitIconSprite.WARPSTONE_MERCHANT


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
    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)
    _register_dialog()
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
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/portrait_warpstone_merchant_npc.png')


def _register_dialog():
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    name = "Tink"
    low_level_dialog = DialogData(
        name=name,
        portrait_icon_sprite=UI_ICON_SPRITE,
        text_body="These aren't any regular old statues! They are magical gateways to distant places! "
                  "I'm extracting their powers into something more ... mobile! "
                  "Just give me a while, and come back later!",
        options=[bye_option])

    mid_level_dialog = DialogData(
        name=name,
        portrait_icon_sprite=UI_ICON_SPRITE,
        text_body="Hah! I managed to infuse the statues' teleporting powers into these stones. " \
                  "You can carry them with you and use them any time you want to return to this place! "
                  "Isn't that neat?",
        options=[buy_consumable_option(ConsumableType.WARP_STONE, 2),
                 bye_option])

    high_level_dialog = DialogData(
        name=name,
        portrait_icon_sprite=UI_ICON_SPRITE,
        text_body="Check it out! These acid bombs should come in handy if you find yourself surrounded!",
        options=[buy_consumable_option(ConsumableType.WARP_STONE, 2),
                 buy_consumable_option(ConsumableType.ACID_BOMB, 4),
                 bye_option])

    def get_dialog_data(game_state: GameState) -> DialogData:
        if game_state.player_state.level >= 4:
            return high_level_dialog
        elif game_state.player_state.level >= 2:
            return mid_level_dialog
        else:
            return low_level_dialog

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
