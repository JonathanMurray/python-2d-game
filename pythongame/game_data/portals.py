from pythongame.core.common import Direction, PortalId
from pythongame.core.game_data import SpriteSheet, Sprite, register_entity_sprite_map, register_portal_data, PortalData

PORTAL_SIZE = (42, 46)


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

    register_portal_data(PortalId.A_BASE, PortalData(False, PortalId.A_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.A_REMOTE, PortalData(True, PortalId.A_BASE, Sprite.PORTAL_BLUE))
    register_portal_data(PortalId.B_BASE, PortalData(False, PortalId.B_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.B_REMOTE, PortalData(True, PortalId.B_BASE, Sprite.PORTAL_RED))
    register_portal_data(PortalId.C_BASE, PortalData(False, PortalId.C_REMOTE, Sprite.PORTAL_DISABLED))
    register_portal_data(PortalId.C_REMOTE, PortalData(True, PortalId.C_BASE, Sprite.PORTAL_DARK))
