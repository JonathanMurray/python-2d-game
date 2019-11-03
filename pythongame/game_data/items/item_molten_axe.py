from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


def register_molten_axe_item():
    item_type = ItemType.MOLTEN_AXE
    damage_bonus = 0.25
    ui_icon_sprite = UiIconSprite.ITEM_MOLTEN_AXE
    sprite = Sprite.ITEM_MOLTEN_AXE
    effect = StatModifyingItemEffect(item_type, {HeroStat.DAMAGE: damage_bonus})
    register_item_effect(item_type, effect)
    image_file_path = "resources/graphics/item_molten_axe.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    description = effect.get_description()
    item_data = ItemData(ui_icon_sprite, sprite, "Molten Axe", description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(item_type, item_data)
