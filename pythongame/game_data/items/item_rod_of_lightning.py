import random

from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import AbilityResult, AbilityWasUsedSuccessfully, register_ability_effect
from pythongame.core.common import ItemType, Millis, Sprite, UiIconSprite, PeriodicTimer, AbilityType
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_state import GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle, VisualLine
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ABILITY_NUM_TARGETS = 3
ABILITY_TYPE = AbilityType.ITEM_ROD_OF_LIGHTNING
ITEM_NAME = "Rod of the Ancients"
ABILITY_DESCRIPTION = f"Strike {ABILITY_NUM_TARGETS} nearby enemies"

MIN_DMG = 1
MAX_DMG = 3


def strike_enemies(game_state: GameState, num_enemies: int):
    player_entity = game_state.game_world.player_entity
    player_center_position = player_entity.get_center_position()
    close_enemies = game_state.game_world.get_enemies_within_x_y_distance_of(140, player_center_position)
    # TODO: sound effect
    for enemy in close_enemies[0: num_enemies]:
        damage_amount: float = MIN_DMG + random.random() * (MAX_DMG - MIN_DMG)
        deal_player_damage_to_enemy(game_state, enemy, damage_amount, DamageType.MAGIC)
        enemy_center_position = enemy.world_entity.get_center_position()
        game_state.game_world.visual_effects.append(
            VisualCircle((250, 250, 0), player_center_position, 50, 140, Millis(100), 1, player_entity))
        game_state.game_world.visual_effects.append(
            VisualLine((250, 250, 0), player_center_position, enemy_center_position, Millis(80), 3))


class ItemEffect(AbstractItemEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(5000))

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            strike_enemies(game_state, 1)


def _apply_ability(game_state: GameState) -> AbilityResult:
    strike_enemies(game_state, ABILITY_NUM_TARGETS)
    return AbilityWasUsedSuccessfully()


def _register_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)

    ability_data = AbilityData(ITEM_NAME, UiIconSprite.ITEM_ROD_OF_LIGHTNING, 15, Millis(10_000), ABILITY_DESCRIPTION,
                               sound_id=None, is_item_ability=True)
    register_ability_data(ABILITY_TYPE, ability_data)


def register_rod_of_lightning_item():
    _register_ability()
    item_type = ItemType.ROD_OF_LIGHTNING
    register_custom_effect_item(
        item_type=item_type,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_ROD_OF_LIGHTNING,
        sprite=Sprite.ITEM_ROD_OF_LIGHTNING,
        image_file_path="resources/graphics/item_rod_of_lightning.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name=ITEM_NAME,
        custom_description=[
            "Periodically deals " + str(MIN_DMG) + "-" + str(MAX_DMG) + " magic damage to one nearby enemy",
            "Active: " + ABILITY_DESCRIPTION],
        stat_modifier_intervals=[],
        custom_effect=ItemEffect(),
        is_unique=True,
        active_ability_type=ABILITY_TYPE
    )
