from pythongame.core.common import UiIconSprite, Direction, Sprite
from pythongame.core.game_data import register_ui_icon_sprite_path, register_entity_sprite_map
from pythongame.core.view.image_loading import SpriteSheet


def register_map_editor_icons():
    register_ui_icon_sprite_path(UiIconSprite.MAP_EDITOR_TRASHCAN, "resources/graphics/icon_trashcan.png")
    register_ui_icon_sprite_path(UiIconSprite.MAP_EDITOR_RECYCLING, "resources/graphics/icon_recycling.png")


def register_map_smart_floor_tile_sprites():
    sprite_sheet = SpriteSheet("resources/graphics/material_tileset.png")
    register_entity_sprite_map(Sprite.MAP_EDITOR_SMART_FLOOR_1, sprite_sheet, (16, 16), (25, 25),
                               {Direction.DOWN: [(8, 8)]}, (0, 0))
    register_entity_sprite_map(Sprite.MAP_EDITOR_SMART_FLOOR_2, sprite_sheet, (16, 16), (50, 50),
                               {Direction.DOWN: [(8, 8)]}, (0, 0))
    register_entity_sprite_map(Sprite.MAP_EDITOR_SMART_FLOOR_3, sprite_sheet, (16, 16), (75, 75),
                               {Direction.DOWN: [(8, 8)]}, (0, 0))
    register_entity_sprite_map(Sprite.MAP_EDITOR_SMART_FLOOR_4, sprite_sheet, (16, 16), (100, 100),
                               {Direction.DOWN: [(8, 8)]}, (0, 0))
