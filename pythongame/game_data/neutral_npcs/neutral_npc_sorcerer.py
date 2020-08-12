import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, ConsumableType, \
    PortraitIconSprite, PeriodicTimer
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, DialogData, \
    DialogOptionData, buy_consumable_option, register_conditional_npc_dialog_data
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.world_entity import WorldEntity

NPC_TYPE = NpcType.NEUTRAL_SORCERER
PORTRAIT_ICON_SPRITE = PortraitIconSprite.SORCERER


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
    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)
    _register_dialog()
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
    register_portrait_icon_sprite_path(PORTRAIT_ICON_SPRITE, 'resources/graphics/portrait_sorcerer_npc.png')


def _register_dialog():
    dialog_options = [
        buy_consumable_option(ConsumableType.HEALTH, 5),
        buy_consumable_option(ConsumableType.MANA, 5),
        buy_consumable_option(ConsumableType.SPEED, 5),
        buy_consumable_option(ConsumableType.POWER, 10),
        buy_consumable_option(ConsumableType.MAGIC_RESIST, 10),
        DialogOptionData("\"Good bye\"", "cancel", None)]
    text_low_level = "Huh?! Well, aren't you the brave one, making it all the way out here! I would think " \
                     "twice before heading down that way! Well since you are here, see if any of these " \
                     "potions are of interest."
    text_high_level = "You are on the doorsteps of the Red Baron's domain! Please be careful. " \
                      "Here, see if any of these potions can be of use."
    name = "Sorcerer"
    dialog_low_level = DialogData(name, PORTRAIT_ICON_SPRITE, text_low_level, dialog_options)
    dialog_high_level = DialogData(name, PORTRAIT_ICON_SPRITE, text_high_level, dialog_options)

    def get_dialog_data(game_state: GameState) -> DialogData:
        if game_state.player_state.level < 5:
            return dialog_low_level
        else:
            return dialog_high_level

    register_conditional_npc_dialog_data(NPC_TYPE, get_dialog_data)
