import random
from typing import Dict, Union, List, Iterable, Optional

from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, plain_item_id, randomized_item_id, \
    ItemSuffix, ItemId
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE, register_item_level, get_item_data
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect, EmptyItemEffect, \
    AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_stat_modifying_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        stat_modifiers: Dict[HeroStat, Union[int, float]],
        item_level: Optional[int] = None):
    item_id = plain_item_id(item_type)
    if item_level is not None:
        register_item_level(item_type, item_level)
    item_effect = StatModifyingItemEffect(item_id, stat_modifiers)
    item_data = ItemData(ui_icon_sprite, sprite, name, item_effect.get_description(), item_equipment_category)
    register_item_effect(item_id, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_id, item_data)


def register_randomized_stat_modifying_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        stat_modifier_intervals: Dict[HeroStat, Union[List[int], List[float]]],
        item_level: Optional[int] = None):
    _register_randomized_stat_modifying_item(
        item_type, item_level, ui_icon_sprite, sprite, image_file_path, item_equipment_category, name,
        _split_stat_modifier_intervals(stat_modifier_intervals))


def _register_randomized_stat_modifying_item(
        item_type: ItemType,
        item_level: Optional[int],
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        multiple_stat_modifiers: List[Dict[HeroStat, Union[int, float]]]):
    if item_level is not None:
        register_item_level(item_type, item_level)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    for i, stat_modifiers in enumerate(multiple_stat_modifiers):
        item_id = randomized_item_id(item_type, i)
        item_effect = StatModifyingItemEffect(item_id, stat_modifiers)
        item_data = ItemData(ui_icon_sprite, sprite, name, item_effect.get_description(), item_equipment_category)
        register_item_effect(item_id, item_effect)
        register_item_data(item_id, item_data)


def register_custom_effect_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        item_effect: AbstractItemEffect,
        item_level: Optional[int] = None):
    item_id = plain_item_id(item_type)
    if item_level is not None:
        register_item_level(item_type, item_level)
    item_data = ItemData(ui_icon_sprite, sprite, name, item_effect.get_description(), item_equipment_category)
    register_item_effect(item_id, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_id, item_data)


def _split_stat_modifier_intervals(randomized_stat_modifiers: Dict[HeroStat, Union[Iterable[int], List[float]]]) \
        -> List[Dict[HeroStat, Union[int, float]]]:
    return _split_stat_modifier_intervals_2(randomized_stat_modifiers, {})


def _split_stat_modifier_intervals_2(
        remaining: Dict[HeroStat, Union[Iterable[int], List[float]]],
        acummulated_dict: Dict[HeroStat, Union[int, float]]) \
        -> List[Dict[HeroStat, Union[int, float]]]:
    if len(remaining) == 0:
        return [acummulated_dict]
    key = list(remaining.keys())[0]
    values = remaining[key]
    del remaining[key]
    result = []
    for value in values:
        inner_dict = dict(acummulated_dict)
        inner_dict[key] = value
        inner_remaining = dict(remaining)
        inner_dicts = _split_stat_modifier_intervals_2(inner_remaining, inner_dict)
        result.extend(inner_dicts)
    return result


def register_passive_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        name: str,
        description_lines: List[str]):
    item_id = plain_item_id(item_type)
    item_effect = EmptyItemEffect(item_id)
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines)
    register_item_effect(item_id, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_id, item_data)


def register_quest_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        name: str,
        description_lines: List[str]):
    item_id = plain_item_id(item_type)
    item_effect = EmptyItemEffect(item_id)
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines, ItemEquipmentCategory.QUEST)
    register_item_effect(item_id, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_id, item_data)


# TODO Finish itemization
def get_random_id(item_type: ItemType, suffix: ItemSuffix) -> ItemId:
    id_string = item_type.name + ":" + suffix.affix_id.name
    for (hero_stat, interval) in suffix.stat_modifier_intervals:
        id_string += "~" + hero_stat.name + "~" + str(random.choice(interval))
    return ItemId(id_string)


def get_stats(item_id: ItemId):
    get_item_data(item_id)
