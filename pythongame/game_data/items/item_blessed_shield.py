from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState, Event, PlayerBlockedEvent
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, healing_amount: int, item_type: ItemType, stat_modifiers):
        super().__init__(item_type, stat_modifiers)
        self.healing_amount = healing_amount

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            player_receive_healing(self.healing_amount, game_state)


def register_blessed_shield_item():
    item_types = [ItemType.BLESSED_SHIELD_1, ItemType.BLESSED_SHIELD_2, ItemType.BLESSED_SHIELD_3]
    healing_amounts = [2, 3, 4]
    armor_boost = 2
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]

        healing_amount = healing_amounts[i]
        stat_modifiers = {HeroStat.ARMOR: armor_boost, HeroStat.BLOCK_AMOUNT: 6}
        effect = ItemEffect(healing_amount, item_type, stat_modifiers)
        register_item_effect(item_type, effect)
        name = "Blessed Shield (" + str(i + 1) + ")"
        description = effect.get_description() + ["On block: gain " + str(healing_amount) + " health"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_type, item_data)
