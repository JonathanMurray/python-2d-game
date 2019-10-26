import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, ConsumableType, \
    PortraitIconSprite, PeriodicTimer
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


def register_sorcerer_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_SORCERER
    portrait_icon_sprite = PortraitIconSprite.SORCERER
    npc_type = NpcType.NEUTRAL_SORCERER
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    dialog_options = [
        buy_consumable_option(ConsumableType.HEALTH, 5),
        buy_consumable_option(ConsumableType.MANA, 5),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    dialog_text_body = "Greetings. I am glad to see that you have made it this far! However, great danger lies ahead... " \
                       "Here, see if any of these potions are of interest to you."
    dialog_data = DialogData(portrait_icon_sprite, dialog_text_body, dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 3
    indices_by_dir = {
        Direction.DOWN: [(x, 4), (x + 1, 4), (x + 2, 4)],
        Direction.LEFT: [(x, 5), (x + 1, 5), (x + 2, 5)],
        Direction.RIGHT: [(x, 6), (x + 1, 6), (x + 2, 6)],
        Direction.UP: [(x, 7), (x + 1, 7), (x + 2, 7)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(portrait_icon_sprite, 'resources/graphics/portrait_sorcerer_npc.png')
