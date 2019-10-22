import random

from pythongame.core.common import ItemType, Sprite, UiIconSprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import GameState, Event, PlayerWasAttackedEvent
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPES = [ItemType.BLESSED_SHIELD_1, ItemType.BLESSED_SHIELD_2, ItemType.BLESSED_SHIELD_3]
PROC_CHANCES = [0.3, 0.4, 0.5]
ARMOR_BOOST = 2


class ItemEffect(AbstractItemEffect):

    def __init__(self, proc_chance: float, item_type: ItemType):
        self.proc_chance = proc_chance
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus -= ARMOR_BOOST

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerWasAttackedEvent):
            if random.random() < self.proc_chance:
                player_receive_healing(1, game_state)

    def get_item_type(self):
        return self.item_type


def register_blessed_shield_item():
    ui_icon_sprite = UiIconSprite.ITEM_BLESSED_SHIELD
    sprite = Sprite.ITEM_BLESSED_SHIELD
    register_ui_icon_sprite_path(ui_icon_sprite, "resources/graphics/item_blessed_shield.png")
    register_entity_sprite_initializer(
        sprite, SpriteInitializer("resources/graphics/item_blessed_shield.png", ITEM_ENTITY_SIZE))
    for i in range(3):
        item_type = ITEM_TYPES[i]
        proc_chance = PROC_CHANCES[i]
        register_item_effect(item_type, ItemEffect(proc_chance, item_type))
        name = "Blessed Shield (" + str(i + 1) + ")"
        description = [str(ARMOR_BOOST) + " armor",
                       "{:.0f}".format(proc_chance * 100) + "% on hit: gain 1 health"]
        item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
        register_item_data(item_type, item_data)
