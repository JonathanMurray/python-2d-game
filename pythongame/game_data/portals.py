from typing import Tuple

from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Direction, PortalId, Millis, BuffType
from pythongame.core.game_data import SpriteSheet, Sprite, register_entity_sprite_map, register_portal_data, PortalData
from pythongame.core.game_state import GameState, WorldEntity, NonPlayerCharacter
from pythongame.core.visual_effects import VisualRect, VisualCircle

PORTAL_SIZE = (42, 46)
BUFF_TYPE = BuffType.BEING_TELEPORTED
PORTAL_DELAY = Millis(600)


class BeingTeleported(AbstractBuffEffect):
    def __init__(self, destination: Tuple[int, int]):
        self.destination = destination
        self.time_since_start = 0
        self.has_teleport_happened = False

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.player_entity.set_not_moving()
        effect_position = buffed_entity.get_center_position()
        color = (140, 140, 230)
        game_state.visual_effects.append(VisualCircle(color, effect_position, 17, 35, Millis(150), 1))
        game_state.visual_effects.append(VisualRect(color, effect_position, 37, 50, Millis(150), 1))
        game_state.visual_effects.append(VisualCircle(color, effect_position, 25, 50, Millis(300), 2))
        game_state.player_entity.visible = False

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self.time_since_start += time_passed
        if not self.has_teleport_happened and self.time_since_start > PORTAL_DELAY / 2:
            self.has_teleport_happened = True
            game_state.player_entity.set_position(self.destination)
            effect_position = buffed_entity.get_center_position()
            color = (140, 140, 230)
            game_state.visual_effects.append(VisualCircle(color, effect_position, 17, 35, Millis(150), 1))
            game_state.visual_effects.append(VisualRect(color, effect_position, 37, 50, Millis(150), 1))
            game_state.visual_effects.append(VisualCircle(color, effect_position, 25, 50, Millis(300), 2))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        game_state.player_entity.visible = True

    def get_buff_type(self):
        return BUFF_TYPE


def register_portal():
    original_sprite_size = (28, 62)
    scaled_sprite_size = (46, 100)
    indices_by_dir = {Direction.DOWN: [(0, 0)]}
    sprite_position_relative_to_entity = (-4, -54)
    register_entity_sprite_map(
        Sprite.PORTAL_DISABLED,
        SpriteSheet("resources/graphics/statue.png"),
        original_sprite_size,
        scaled_sprite_size,
        indices_by_dir,
        sprite_position_relative_to_entity)
    register_entity_sprite_map(
        Sprite.PORTAL_BLUE,
        SpriteSheet("resources/graphics/statue_blue.png"),
        original_sprite_size,
        scaled_sprite_size,
        indices_by_dir,
        sprite_position_relative_to_entity)
    register_entity_sprite_map(
        Sprite.PORTAL_RED,
        SpriteSheet("resources/graphics/statue_red.png"),
        original_sprite_size,
        scaled_sprite_size,
        indices_by_dir,
        sprite_position_relative_to_entity)
    register_entity_sprite_map(
        Sprite.PORTAL_DARK,
        SpriteSheet("resources/graphics/statue_dark.png"),
        original_sprite_size,
        scaled_sprite_size,
        indices_by_dir,
        sprite_position_relative_to_entity)

    register_portal_data(PortalId.A_BASE, _data(False, PortalId.A_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.A_REMOTE, _data(True, PortalId.A_BASE, Sprite.PORTAL_BLUE))
    register_portal_data(PortalId.B_BASE, _data(False, PortalId.B_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.B_REMOTE, _data(True, PortalId.B_BASE, Sprite.PORTAL_RED))
    register_portal_data(PortalId.C_BASE, _data(False, PortalId.C_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.C_REMOTE, _data(True, PortalId.C_BASE, Sprite.PORTAL_DARK))

    register_buff_effect(BUFF_TYPE, BeingTeleported)


def _data(starts_enabled: bool, portal_id: PortalId, sprite: Sprite):
    return PortalData(starts_enabled, portal_id, sprite, PORTAL_SIZE, PORTAL_DELAY)
