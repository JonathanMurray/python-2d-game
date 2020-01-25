from typing import Dict, Union, List

from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, plain_item_id, randomized_item_id
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
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
        stat_modifiers: Dict[HeroStat, Union[int, float]]):
    item_effect = StatModifyingItemEffect(plain_item_id(item_type), stat_modifiers)
    item_data = ItemData(ui_icon_sprite, sprite, name, item_effect.get_description(), item_equipment_category)
    register_item_effect(item_type, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_type, item_data)


def register_randomized_stat_modifying_item(
        item_type: ItemType,
        ui_icon_sprite: UiIconSprite,
        sprite: Sprite,
        image_file_path: str,
        item_equipment_category: ItemEquipmentCategory,
        name: str,
        randomized_stat_modifiers: List[Dict[HeroStat, Union[int, float]]]):
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    for i, stat_modifiers in enumerate(randomized_stat_modifiers):
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
        item_effect: AbstractItemEffect):
    item_data = ItemData(ui_icon_sprite, sprite, name, item_effect.get_description(), item_equipment_category)
    register_item_effect(item_type, item_effect)
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
    item_effect = EmptyItemEffect(item_type)
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines)
    register_item_effect(item_type, item_effect)
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
    item_effect = EmptyItemEffect(item_type)
    item_data = ItemData(ui_icon_sprite, sprite, name, description_lines, ItemEquipmentCategory.QUEST)
    register_item_effect(item_type, item_effect)
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_data(item_type, item_data)
