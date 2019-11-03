import random

from pythongame.core.common import ItemType, Sprite, HeroStat
from pythongame.core.damage_interactions import deal_player_damage_to_enemy
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, PlayerLostHealthEvent, GameState
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

PROC_CHANCE = 0.25
DAMAGE = 5


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, item_type: ItemType, stat_modifiers):
        super().__init__(item_type, stat_modifiers)

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerLostHealthEvent):
            if event.npc_attacker and random.random() < PROC_CHANCE:
                deal_player_damage_to_enemy(game_state, event.npc_attacker, DAMAGE)


def register_skull_shield_item():
    item_type = ItemType.SKULL_SHIELD
    armor_boost = 2
    ui_icon_sprite = UiIconSprite.ITEM_SKULL_SHIELD
    sprite = Sprite.ITEM_SKULL_SHIELD
    image_file_path = "resources/graphics/item_skull_shield.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    effect = ItemEffect(item_type, {HeroStat.ARMOR: armor_boost})
    register_item_effect(item_type, effect)
    name = "Skull shield"
    description = effect.get_description() + \
                  ["{:.0f}".format(PROC_CHANCE * 100) + "% on hit: deal " + str(DAMAGE) + " damage to attacker"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
    register_item_data(item_type, item_data)
