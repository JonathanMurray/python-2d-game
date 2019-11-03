from typing import Dict, Union, List

from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect, EmptyItemEffect
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
    item_effect = StatModifyingItemEffect(item_type, stat_modifiers)
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
