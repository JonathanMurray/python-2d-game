from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory


def register_orb_of_the_magi_item():
    item_types = [ItemType.ORB_OF_THE_MAGI_1, ItemType.ORB_OF_THE_MAGI_2, ItemType.ORB_OF_THE_MAGI_3]
    multiplier_bonuses = [0.1, 0.15, 0.2]
    ui_icon_sprite = UiIconSprite.ITEM_ORB_OF_THE_MAGI
    sprite = Sprite.ITEM_ORB_OF_THE_MAGI
    image_file_path = "resources/graphics/item_orb_of_the_magi.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(
        sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]
        bonus = multiplier_bonuses[i]
        effect = StatModifyingItemEffect(item_type, {HeroStat.DAMAGE: bonus})
        register_item_effect(item_type, effect)
        name = "Orb of the Magi (" + str(i + 1) + ")"
        description = ["+" + str(int(round(bonus * 100))) + "% damage"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_type, item_data)
