from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat, randomized_item_id, ItemId
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE, register_item_level
from pythongame.core.game_state import GameState, Event, PlayerBlockedEvent
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, healing_amount: int, item_id: ItemId, stat_modifiers):
        super().__init__(item_id, stat_modifiers)
        self.healing_amount = healing_amount

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            player_receive_healing(self.healing_amount, game_state)


def register_blessed_shield_item():
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    register_item_level(ItemType.BLESSED_SHIELD, 3)
    for i, healing_amount in enumerate([2, 3, 4, 5]):
        item_id = randomized_item_id(ItemType.BLESSED_SHIELD, i)
        effect = ItemEffect(healing_amount, item_id, {HeroStat.ARMOR: 2, HeroStat.BLOCK_AMOUNT: 6})
        register_item_effect(item_id, effect)
        item_data = ItemData(
            icon_sprite=ui_icon_sprite,
            entity_sprite=sprite,
            name="Blessed Shield",
            description_lines=effect.get_description() + ["On block: gain " + str(healing_amount) + " health"],
            item_equipment_category=ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_id, item_data)
