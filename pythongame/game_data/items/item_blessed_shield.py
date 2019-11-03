import random

from pythongame.core.common import ItemType, Sprite, UiIconSprite, HeroStat
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState, Event, PlayerWasAttackedEvent
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, proc_chance: float, item_type: ItemType, stat_modifiers):
        super().__init__(item_type, stat_modifiers)
        self.proc_chance = proc_chance

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerWasAttackedEvent):
            if random.random() < self.proc_chance:
                player_receive_healing(1, game_state)


def register_blessed_shield_item():
    item_types = [ItemType.BLESSED_SHIELD_1, ItemType.BLESSED_SHIELD_2, ItemType.BLESSED_SHIELD_3]
    proc_chances = [0.3, 0.4, 0.5]
    armor_boost = 2
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = item_types[i]
        proc_chance = proc_chances[i]
        register_item_effect(item_type, ItemEffect(proc_chance, item_type, {HeroStat.ARMOR: armor_boost}))
        name = "Blessed Shield (" + str(i + 1) + ")"
        description = [str(armor_boost) + " armor",
                       "{:.0f}".format(proc_chance * 100) + "% on hit: gain 1 health"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_type, item_data)
