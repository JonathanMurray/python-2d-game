import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, ConsumableType, \
    PortraitIconSprite, PeriodicTimer
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, DialogData, \
    DialogOptionData, buy_consumable_option, register_conditional_npc_dialog_data
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.world_entity import WorldEntity

NPC_TYPE = NpcType.NEUTRAL_NINJA
PORTRAIT_ICON_SPRITE = PortraitIconSprite.NINJA


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


def register_ninja_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_NINJA

    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)

    _register_dialog()

    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 6
    indices_by_dir = {
        Direction.DOWN: [(x, 0), (x + 1, 0), (x + 2, 0)],
        Direction.LEFT: [(x, 1), (x + 1, 1), (x + 2, 1)],
        Direction.RIGHT: [(x, 2), (x + 1, 2), (x + 2, 2)],
        Direction.UP: [(x, 3), (x + 1, 3), (x + 2, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(PORTRAIT_ICON_SPRITE, 'resources/graphics/ninja_portrait.png')


def _register_dialog():
    dialog_text_body = "Ah.. You're new here, aren't you? Interested in my stock of potions? They come at a price of course..."
    consumables_1 = [
        buy_consumable_option(ConsumableType.BREW, 2),
        buy_consumable_option(ConsumableType.HEALTH_LESSER, 3),
        buy_consumable_option(ConsumableType.MANA_LESSER, 3)
    ]
    consumables_2 = [
        buy_consumable_option(ConsumableType.SPEED, 4),
        buy_consumable_option(ConsumableType.POWER, 10)
    ]
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)

    name = "Zak"
    dialog_low_level = DialogData(name, PORTRAIT_ICON_SPRITE, dialog_text_body, consumables_1 + [bye_option])
    dialog_high_level = DialogData(name, PORTRAIT_ICON_SPRITE, dialog_text_body,
                                   consumables_1 + consumables_2 + [bye_option])

    def get_dialog_data(game_state: GameState) -> DialogData:
        if game_state.player_state.level < 3:
            return dialog_low_level
        else:
            return dialog_high_level

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
