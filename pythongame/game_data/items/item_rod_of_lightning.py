import random

from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, PeriodicTimer
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle, VisualLine
from pythongame.game_data.items.register_items_util import register_custom_effect_item


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        super().__init__(item_type)
        self.timer = PeriodicTimer(Millis(5000))
        self.min_dmg = 1
        self.max_dmg = 3

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            player_entity = game_state.player_entity
            player_center_position = player_entity.get_center_position()
            close_enemies = game_state.get_enemies_within_x_y_distance_of(140, player_center_position)
            if close_enemies:
                damage_amount: float = self.min_dmg + random.random() * (self.max_dmg - self.min_dmg)
                deal_player_damage_to_enemy(game_state, close_enemies[0], damage_amount, DamageType.MAGIC)
                enemy_center_position = close_enemies[0].world_entity.get_center_position()
                game_state.visual_effects.append(
                    VisualCircle((250, 250, 0), player_center_position, 50, 140, Millis(100), 1, player_entity))
                game_state.visual_effects.append(
                    VisualLine((250, 250, 0), player_center_position, enemy_center_position, Millis(80), 3))

    def get_description(self):
        return ["Periodically deals" + str(self.min_dmg) + "-" + str(self.max_dmg) + " magic damage to nearby enemies"]


def register_rod_of_lightning_item():
    item_type = ItemType.ROD_OF_LIGHTNING
    register_custom_effect_item(
        item_type=item_type,
        ui_icon_sprite=UiIconSprite.ITEM_ROD_OF_LIGHTNING,
        sprite=Sprite.ITEM_ROD_OF_LIGHTNING,
        image_file_path="resources/graphics/item_rod_of_lightning.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Rod of Lightning",
        item_effect=ItemEffect(item_type)
    )
