import random

from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle, VisualLine
from pythongame.game_data.items.register_items_util import register_custom_effect_item

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
                deal_player_damage_to_enemy(game_state, close_enemies[0], damage_amount, DamageType.MAGIC)
                enemy_center_position = close_enemies[0].world_entity.get_center_position()
                game_state.visual_effects.append(
                    VisualCircle((250, 250, 0), player_center_position, 50, 140, Millis(100), 1, player_entity))
                game_state.visual_effects.append(
                    VisualLine((250, 250, 0), player_center_position, enemy_center_position, Millis(80), 3))


def register_rod_of_lightning_item():
    item_type = ItemType.ROD_OF_LIGHTNING
    register_custom_effect_item(
        item_type=item_type,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ROD_OF_LIGHTNING,
        sprite=Sprite.ITEM_ROD_OF_LIGHTNING,
        image_file_path="resources/graphics/item_rod_of_lightning.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Rod of Lightning",
        custom_description=[
            "Periodically deals " + str(MIN_DMG) + "-" + str(MAX_DMG) + " magic damage to nearby enemies"],
        stat_modifier_intervals=[],
        custom_effect=ItemEffect()
    )
