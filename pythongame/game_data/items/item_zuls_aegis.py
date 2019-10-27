import random

from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, PlayerLostHealthEvent, GameState, WorldEntity, \
    NonPlayerCharacter
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle

STUN_DURATION = Millis(1500)

ITEM_TYPE = ItemType.ZULS_AEGIS
BUFF_TYPE_STUNNED = BuffType.STUNNED_BY_AEGIS_ITEM
PROC_CHANCE = 0.2
ARMOR_BOOST = 2


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus -= ARMOR_BOOST

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerLostHealthEvent):
            if event.npc_attacker and random.random() < PROC_CHANCE:
                event.npc_attacker.gain_buff_effect(get_buff_effect(BUFF_TYPE_STUNNED), STUN_DURATION)

    def get_item_type(self):
        return self.item_type


class StunnedFromAegis(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        visual_effect = VisualCircle((220, 220, 50), buffed_entity.get_center_position(), 9, 16, Millis(250), 2)
        game_state.visual_effects.append(visual_effect)
        buffed_npc.stun_status.add_one()
        buffed_entity.set_not_moving()

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_npc.stun_status.remove_one()

    def get_buff_type(self):
        return BUFF_TYPE_STUNNED


def register_zuls_aegis():
    ui_icon_sprite = UiIconSprite.ITEM_ZULS_AEGIS
    sprite = Sprite.ITEM_ZULS_AEGIS
    image_file_path = "resources/graphics/item_zuls_aegis.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect(ITEM_TYPE))
    name = "Zul's Aegis"
    description = [str(ARMOR_BOOST) + " armor",
                   "{:.0f}".format(PROC_CHANCE * 100) + "% on hit: stun attacker for " \
                   + "{:.1f}".format(STUN_DURATION / 1000) + "s"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
    register_item_data(ITEM_TYPE, item_data)
    register_buff_effect(BUFF_TYPE_STUNNED, StunnedFromAegis)
