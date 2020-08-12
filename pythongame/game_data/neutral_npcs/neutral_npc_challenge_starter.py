import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer, ItemType
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.item_data import randomized_item_id
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, register_npc_dialog_data, DialogData, \
    DialogOptionData, buy_item_option
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.world_entity import WorldEntity


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


def register_challenge_starter_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_CHALLENGE_STARTER
    portrait_icon_sprite = PortraitIconSprite.CHALLENGE_STARTER
    npc_type = NpcType.NEUTRAL_CHALLENGE_STARTER
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)

    dialog_options = [
        buy_item_option(randomized_item_id(ItemType.GLADIATOR_ARMOR), 20),
        buy_item_option(randomized_item_id(ItemType.HEALING_WAND), 20),
        buy_item_option(randomized_item_id(ItemType.ZULS_AEGIS), 20),
        buy_item_option(randomized_item_id(ItemType.WARLOCKS_COWL), 20),
        buy_item_option(randomized_item_id(ItemType.DRUIDS_RING), 20),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    dialog_text_body = "Choose wisely."
    dialog_data = DialogData("Vendor", portrait_icon_sprite, dialog_text_body, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
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
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/ninja_portrait.png')
