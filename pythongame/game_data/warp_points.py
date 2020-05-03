from typing import Tuple

from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect
from pythongame.core.common import Direction, PLAYER_ENTITY_SIZE, Millis, BuffType, SoundId
from pythongame.core.entity_creation import create_warp_point
from pythongame.core.game_data import Sprite, register_entity_sprite_map
from pythongame.core.game_state import GameState, NonPlayerCharacter
from pythongame.core.sound_player import play_sound
from pythongame.core.view.image_loading import SpriteSheet
from pythongame.core.visual_effects import create_teleport_effects
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.portals import PORTAL_DELAY

WARP_STONE_BUFF = BuffType.TELEPORTING_WITH_WARP_STONE
WARP_POINT_BUFF = BuffType.TELEPORTING_WITH_WARP_POINT


class TeleportingWithWarpStone(AbstractBuffEffect):
    def __init__(self, destination: Tuple[int, int]):
        self.destination = destination
        self.time_since_start = 0
        self.has_teleport_happened = False

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        player_entity = game_state.game_world.player_entity
        player_entity.set_not_moving()
        player_entity.visible = False
        game_state.game_world.visual_effects += create_teleport_effects(buffed_entity.get_center_position())
        player_collision_rect = (player_entity.pygame_collision_rect.w, player_entity.pygame_collision_rect.h)
        home_warp_point = create_warp_point(game_state.player_spawn_position, player_collision_rect)
        remote_warp_point = create_warp_point(player_entity.get_center_position(), player_collision_rect)
        game_state.game_world.warp_points = [home_warp_point, remote_warp_point]

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self.time_since_start += time_passed
        if not self.has_teleport_happened and self.time_since_start > PORTAL_DELAY / 2:
            self.has_teleport_happened = True
            for warp_point in game_state.game_world.warp_points:
                warp_point.make_visible()
            game_state.game_world.player_entity.set_position(self.destination)
            game_state.game_world.visual_effects += create_teleport_effects(buffed_entity.get_center_position())

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        game_state.game_world.player_entity.visible = True

    def get_buff_type(self):
        return WARP_STONE_BUFF


class TeleportingWithWarpPoint(AbstractBuffEffect):
    def __init__(self, destination: Tuple[int, int]):
        self.destination = destination
        self.time_since_start = 0
        self.has_teleport_happened = False

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.add_one()
        game_state.game_world.player_entity.set_not_moving()
        game_state.game_world.player_entity.visible = False
        game_state.game_world.visual_effects += create_teleport_effects(buffed_entity.get_center_position())

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        self.time_since_start += time_passed
        if not self.has_teleport_happened and self.time_since_start > PORTAL_DELAY / 2:
            self.has_teleport_happened = True
            game_state.game_world.warp_points = []
            game_state.game_world.player_entity.set_position(self.destination)
            game_state.game_world.visual_effects += create_teleport_effects(buffed_entity.get_center_position())
            play_sound(SoundId.WARP)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.stun_status.remove_one()
        game_state.game_world.player_entity.visible = True

    def get_buff_type(self):
        return WARP_STONE_BUFF


def register_warp_point():
    original_sprite_size = (640, 640)
    scaled_sprite_size = (40, 40)
    indices_by_dir = {Direction.DOWN: [(x, 0) for x in range(6)]}
    sprite_position_relative_to_entity = (
        (PLAYER_ENTITY_SIZE[0] - scaled_sprite_size[0]) / 2,
        (PLAYER_ENTITY_SIZE[1] - scaled_sprite_size[1]) / 2
    )
    register_entity_sprite_map(
        Sprite.WARP_POINT,
        SpriteSheet("resources/graphics/animated_warppoint.png"),
        original_sprite_size,
        scaled_sprite_size,
        indices_by_dir,
        sprite_position_relative_to_entity)
    register_buff_effect(WARP_STONE_BUFF, TeleportingWithWarpStone)
    register_buff_effect(WARP_POINT_BUFF, TeleportingWithWarpPoint)
