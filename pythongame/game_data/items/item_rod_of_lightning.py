import random

from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle, VisualLine

ITEM_TYPE = ItemType.ROD_OF_LIGHTNING
MIN_DMG = 1
MAX_DMG = 3


class ItemEffect(AbstractItemEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(5000))

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            player_entity = game_state.player_entity
            player_center_position = player_entity.get_center_position()
            close_enemies = game_state.get_enemies_within_x_y_distance_of(140, player_center_position)
            if close_enemies:
                damage_amount: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
                deal_player_damage_to_enemy(game_state, close_enemies[0], damage_amount)
                enemy_center_position = close_enemies[0].world_entity.get_center_position()
                game_state.visual_effects.append(
                    VisualCircle((250, 250, 0), player_center_position, 50, 140, Millis(100), 1, player_entity))
                game_state.visual_effects.append(
                    VisualLine((250, 250, 0), player_center_position, enemy_center_position, Millis(80), 3))

    def get_item_type(self):
        return ITEM_TYPE


def register_rod_of_lightning_item():
    ui_icon_sprite = UiIconSprite.ITEM_ROD_OF_LIGHTNING
    sprite = Sprite.ITEM_ROD_OF_LIGHTNING
    register_item_effect(ITEM_TYPE, ItemEffect())
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_rod_of_lightning.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_rod_of_lightning.png", ITEM_ENTITY_SIZE))
    description = ["Periodically damages nearby enemies (" + str(MIN_DMG) + "-" + str(MAX_DMG) + ")"]
    item_data = ItemData(ui_icon_sprite, sprite, "Rod of Lightning", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
