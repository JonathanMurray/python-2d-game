import random
from typing import Optional

from pythongame.core.common import NpcType, Sprite, Direction, Millis, get_all_directions, PortraitIconSprite, \
    UiIconSprite
from pythongame.core.game_data import register_npc_data, NpcData, SpriteSheet, register_entity_sprite_map, \
    register_portrait_icon_sprite_path
from pythongame.core.game_state import GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.npc_behaviors import register_npc_behavior, AbstractNpcMind, AbstractNpcAction, \
    register_npc_dialog_data, DialogData, DialogOptionData
from pythongame.core.pathfinding.grid_astar_pathfinder import GlobalPathFinder
from pythongame.core.visual_effects import create_visual_healing_text


class NpcMind(AbstractNpcMind):
    def __init__(self, global_path_finder: GlobalPathFinder):
        super().__init__(global_path_finder)
        self._update_path_interval = 500
        self._time_since_updated_path = self._update_path_interval

    def control_npc(self, game_state: GameState, npc: NonPlayerCharacter, player_entity: WorldEntity,
                    is_player_invisible: bool, time_passed: Millis):
        self._time_since_updated_path += time_passed
        if self._time_since_updated_path > self._update_path_interval:
            self._time_since_updated_path = 0
            if random.random() < 0.8:
                npc.world_entity.set_not_moving()
            else:
                direction = random.choice(get_all_directions())
                npc.world_entity.set_moving_in_dir(direction)


class NpcAction(AbstractNpcAction):

    def act(self, game_state: GameState) -> Optional[str]:
        missing_health = game_state.player_state.max_health - game_state.player_state.health
        if missing_health > 0:
            game_state.visual_effects.append(create_visual_healing_text(game_state.player_entity, missing_health))
            game_state.player_state.gain_full_health()
            return "You feel healthy again!"
        return "Nice..."


def register_nomad_npc():
    size = (30, 30)  # Must not align perfectly with grid cell size (pathfinding issues)
    sprite = Sprite.NEUTRAL_NPC_NOMAD
    npc_type = NpcType.NEUTRAL_NOMAD
    movement_speed = 0.03
    register_npc_data(npc_type, NpcData.neutral(sprite, size, movement_speed))
    register_npc_behavior(npc_type, NpcMind)
    # TODO Use proper icon for 'cancel' option
    dialog_options = [
        DialogOptionData("Accept blessing", "gain full health", NpcAction(), UiIconSprite.POTION_HEALTH),
        DialogOptionData("\"Good bye\"", "cancel", None, UiIconSprite.MAP_EDITOR_TRASHCAN)]
    dialog_data = DialogData(PortraitIconSprite.NOMAD, "Blessings to you fellow traveler.", dialog_options)
    register_npc_dialog_data(npc_type, dialog_data)
    sprite_sheet = SpriteSheet("resources/graphics/enemy_sprite_sheet_3.png")
    original_sprite_size = (32, 32)
    scaled_sprite_size = (48, 48)
    indices_by_dir = {
        Direction.DOWN: [(3, 0), (4, 0), (5, 0)],
        Direction.LEFT: [(3, 1), (4, 1), (5, 1)],
        Direction.RIGHT: [(3, 2), (4, 2), (5, 2)],
        Direction.UP: [(3, 3), (4, 3), (5, 3)]
    }
    register_entity_sprite_map(sprite, sprite_sheet, original_sprite_size, scaled_sprite_size, indices_by_dir,
                               (-8, -16))
    register_portrait_icon_sprite_path(PortraitIconSprite.NOMAD, 'resources/graphics/nomad_portrait.png')
