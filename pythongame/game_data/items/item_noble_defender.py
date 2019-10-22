from pythongame.core.buff_effects import AbstractBuffEffect, register_buff_effect, get_buff_effect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, SpriteInitializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, GameState, WorldEntity, \
    NonPlayerCharacter, PlayerWasAttackedEvent
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory

ITEM_TYPE = ItemType.NOBLE_DEFENDER
BUFF_TYPE_SLOWED = BuffType.SLOWED_FROM_NOBLE_DEFENDER
ARMOR_BOOST = 4
SLOW_AMOUNT = 0.3
SLOW_DURATION = Millis(1500)


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        self.item_type = item_type

    def apply_start_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus += ARMOR_BOOST

    def apply_end_effect(self, game_state: GameState):
        game_state.player_state.armor_bonus -= ARMOR_BOOST

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerWasAttackedEvent):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_SLOWED), SLOW_DURATION)

    def get_item_type(self):
        return self.item_type


class SlowedFromNobleDefender(AbstractBuffEffect):

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(-SLOW_AMOUNT)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(SLOW_AMOUNT)

    def get_buff_type(self):
        return BUFF_TYPE_SLOWED


def register_noble_defender():
    ui_icon_sprite = UiIconSprite.ITEM_NOBLE_DEFENDER
    sprite = Sprite.ITEM_NOBLE_DEFENDER
    image_file_path = "resources/graphics/item_noble_defender.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect(ITEM_TYPE))
    name = "Noble defender"
    description = [str(ARMOR_BOOST) + " armor",
                   "On hit: your movement speed is slowed by {:.0f}".format(SLOW_AMOUNT * 100) + "% for " \
                   + "{:.1f}".format(SLOW_DURATION / 1000) + "s"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
    register_item_data(ITEM_TYPE, item_data)
    register_buff_effect(BUFF_TYPE_SLOWED, SlowedFromNobleDefender)
