import random

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    PeriodicTimer
from pythongame.core.game_data import register_npc_data, NpcData, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, DialogData, \
    DialogOptionData, register_npc_dialog_data, reset_talents_option
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.view.image_loading import SpriteSheet

NPC_TYPE = NpcType.NEUTRAL_TALENT_MASTER
UI_ICON_SPRITE = PortraitIconSprite.TALENT_MASTER


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


def register_talent_master_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_TALENT_MASTER
    movement_speed = 0.03
    register_npc_data(NPC_TYPE, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(NPC_TYPE, NpcMind)
    _register_dialog()
    sprite_sheet = SpriteSheet("resources/graphics/characters_midona_spritesheet.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    x = 9
    y = 0
    indices_by_dir = {
        Direction.DOWN: [(x, y), (x + 1, y), (x + 2, y)],
        Direction.LEFT: [(x, y + 1), (x + 1, y + 1), (x + 2, y + 1)],
        Direction.RIGHT: [(x, y + 2), (x + 1, y + 2), (x + 2, y + 2)],
        Direction.UP: [(x, y + 3), (x + 1, y + 3), (x + 2, y + 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-9, -18))
    register_portrait_icon_sprite_path(UI_ICON_SPRITE, 'resources/graphics/portrait_talent_master_npc.png')


def _register_dialog():
    bye_option = DialogOptionData("\"Good bye\"", "cancel", None)
    name = "Oracle"

    dialog = DialogData(
        name=name,
        portrait_icon_sprite=UI_ICON_SPRITE,
        text_body="Greetings. Do you seek a new path in life? Anything is possible, for the right price.",
        options=[reset_talents_option(25), bye_option],
    )

    register_npc_dialog_data(NPC_TYPE, dialog)
