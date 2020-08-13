from typing import Dict, Union, List, Optional

from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, AbilityType
from pythongame.core.game_data import register_ui_icon_sprite_path, \
    register_entity_sprite_initializer
from pythongame.core.item_data import ItemData, register_item_level, ITEM_ENTITY_SIZE
from pythongame.core.item_data import register_item_data
from pythongame.core.item_effects import register_custom_item_effect, AbstractItemEffect, \
    StatModifierInterval
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_randomized_stat_modifying_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        stat_modifier_intervals: Union[List[StatModifierInterval], Dict[HeroStat, List[Union[int, float]]]],
        item_level: Optional[int] = None,
        is_unique: bool = False):
    if item_level is not None:
        register_item_level(item_type, item_level)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))

    # This is legacy. TODO: only allow list arg
    if isinstance(stat_modifier_intervals, dict):
        stat_modifier_intervals = [StatModifierInterval(hero_stat, stat_modifier_intervals[hero_stat])
                                   for hero_stat in stat_modifier_intervals]

    item_data = ItemData(ui_icon_sprite, sprite, name, [], stat_modifier_intervals, is_unique=is_unique,
                         item_equipment_category=item_equipment_category)
    register_item_data(item_type, item_data)


def register_custom_effect_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        custom_effect: AbstractItemEffect,
        custom_description: List[str],
        stat_modifier_intervals: List[StatModifierInterval],
        item_level: Optional[int] = None,
        is_unique: bool = False,
        active_ability_type: Optional[AbilityType] = None):
    if item_level is not None:
        register_item_level(item_type, item_level)
    item_data = ItemData(ui_icon_sprite, sprite, name, custom_description, stat_modifier_intervals,
                         is_unique=is_unique, item_equipment_category=item_equipment_category,
                         active_ability_type=active_ability_type)
    register_custom_item_effect(item_type, custom_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_type, item_data)


def register_passive_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        name: str,
        description_lines: List[str]):
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines, [], is_unique=False,
                         item_equipment_category=None)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_type, item_data)


def register_quest_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        name: str,
        description_lines: List[str]):
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines, [],
                         is_unique=False, item_equipment_category=ItemEquipmentCategory.QUEST)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_type, item_data)
