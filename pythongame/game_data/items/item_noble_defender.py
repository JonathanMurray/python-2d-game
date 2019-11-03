from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, HeroStat
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, GameState, PlayerWasAttackedEvent
from pythongame.core.item_effects import register_item_effect, StatModifyingItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

BUFF_TYPE_SLOWED = BuffType.SLOWED_FROM_NOBLE_DEFENDER
SLOW_AMOUNT = 0.3
SLOW_DURATION = Millis(1500)


class ItemEffect(StatModifyingItemEffect):

    def __init__(self, item_type: ItemType, stat_modifiers):
        super().__init__(item_type, stat_modifiers)

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerWasAttackedEvent):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE_SLOWED), SLOW_DURATION)


class SlowedFromNobleDefender(StatModifyingBuffEffect):

    def __init__(self):
        super().__init__(BUFF_TYPE_SLOWED, {HeroStat.MOVEMENT_SPEED: -SLOW_AMOUNT})


def register_noble_defender():
    item_type = ItemType.NOBLE_DEFENDER
    armor_boost = 4
    ui_icon_sprite = UiIconSprite.ITEM_NOBLE_DEFENDER
    sprite = Sprite.ITEM_NOBLE_DEFENDER
    image_file_path = "resources/graphics/item_noble_defender.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    effect = ItemEffect(item_type, {HeroStat.ARMOR: armor_boost, HeroStat.BLOCK_AMOUNT: 10})
    register_item_effect(item_type, effect)
    name = "Noble defender"
    description = effect.get_description() + \
                  ["When you are attacked, your movement speed is slowed by {:.0f}".format(SLOW_AMOUNT * 100) +
                   "% for " + "{:.1f}".format(SLOW_DURATION / 1000) + "s"]

    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.OFF_HAND)
    register_item_data(item_type, item_data)
    register_buff_effect(BUFF_TYPE_SLOWED, SlowedFromNobleDefender)
