from pythongame.core.common import UiIconSprite
from pythongame.core.game_data import register_ui_icon_sprite_path


def register_ui_icons():
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_HELMET,
                                 "resources/graphics/inventory_template_helmet.png")
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_CHEST,
                                 "resources/graphics/inventory_template_chest.png")
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_MAINHAND,
                                 "resources/graphics/inventory_template_mainhand.png")
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_OFFHAND,
                                 "resources/graphics/inventory_template_offhand.png")
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_NECK,
                                 "resources/graphics/inventory_template_neck.png")
    register_ui_icon_sprite_path(UiIconSprite.INVENTORY_TEMPLATE_RING,
                                 "resources/graphics/inventory_template_ring.png")
