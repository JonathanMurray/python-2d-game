from pythongame.core.game_data import register_ui_icon_sprite_path, UiIconSprite


def register_map_editor_icons():
    register_ui_icon_sprite_path(UiIconSprite.MAP_EDITOR_TRASHCAN, "resources/graphics/icon_trashcan.png")
    register_ui_icon_sprite_path(UiIconSprite.MAP_EDITOR_RECYCLING, "resources/graphics/icon_recycling.png")
