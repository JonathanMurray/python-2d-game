import random

from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ItemType, Sprite, Millis, PeriodicTimer, BuffType
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE, register_buff_text
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState, NonPlayerCharacter, WorldEntity
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer
from pythongame.core.visual_effects import VisualCircle

ITEM_TYPE = ItemType.STONE_AMULET
PROC_CHANCE = 0.2
ARMOR_BONUS = 10
BUFF_TYPE = BuffType.PROTECTED_BY_STONE_AMULET
BUFF_DURATION = Millis(3000)


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < PROC_CHANCE:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)

    def get_item_type(self):
        return ITEM_TYPE


class ProtectedByStoneAmulet(AbstractBuffEffect):

    def __init__(self):
        self.timer = PeriodicTimer(Millis(300))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.armor_bonus += ARMOR_BONUS

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.visual_effects.append(
                VisualCircle((130, 100, 60), buffed_entity.get_center_position(), 20, 40, Millis(100), 1,
                             buffed_entity))

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        game_state.player_state.armor_bonus -= ARMOR_BONUS

    def get_buff_type(self):
        return BUFF_TYPE


def register_stone_amulet_item():
    ui_icon_sprite = UiIconSprite.ITEM_STONE_AMULET
    sprite = Sprite.ITEM_STONE_AMULET
    image_file_path = "resources/graphics/item_stone_amulet.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect())
    name = "Stone Amulet"
    description = [str(int(PROC_CHANCE * 100)) + "% on kill: gain " + str(ARMOR_BONUS) + " armor for " +
                   "{:.0f}".format(BUFF_DURATION / 1000) + "s"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.NECK)
    register_item_data(ITEM_TYPE, item_data)
    register_buff_effect(BUFF_TYPE, ProtectedByStoneAmulet)
    register_buff_text(BUFF_TYPE, "Protected")
