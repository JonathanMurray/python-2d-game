from pythongame.core.game_data import register_portrait_icon_sprite_path, PortraitIconSprite


def register_portrait_icons():
    register_portrait_icon_sprite_path(PortraitIconSprite.PLAYER, 'resources/graphics/player_portrait.gif')
    register_portrait_icon_sprite_path(PortraitIconSprite.VIKING, 'resources/graphics/viking_portrait.png')
