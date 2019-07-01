from pythongame.core.game_data import register_portrait_icon_sprite_path, PortraitIconSprite


# TODO register these along with the rest of the data belonging to the corresponding entities

def register_portrait_icons():
    register_portrait_icon_sprite_path(PortraitIconSprite.PLAYER, 'resources/graphics/player_portrait.gif')
    register_portrait_icon_sprite_path(PortraitIconSprite.VIKING, 'resources/graphics/viking_portrait.png')
    register_portrait_icon_sprite_path(PortraitIconSprite.NOMAD, 'resources/graphics/nomad_portrait.png')
    register_portrait_icon_sprite_path(PortraitIconSprite.NINJA, 'resources/graphics/ninja_portrait.png')
