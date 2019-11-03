from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, StatModifyingBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, HeroStat
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE, register_buff_text
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.view.image_loading import SpriteInitializer

BUFF_TYPE = BuffType.BUFFED_BY_HEALING_WAND
HEALTH_REGEN_BONUS = 1
BUFF_DURATION = Millis(3000)


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        self.item_type = item_type

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)

    def get_item_type(self):
        return self.item_type


class BuffedByHealingWand(StatModifyingBuffEffect):
    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.HEALTH_REGEN: HEALTH_REGEN_BONUS})


def register_healing_wand_item():
    item_type = ItemType.HEALING_WAND
    ui_icon_sprite = UiIconSprite.ITEM_HEALING_WAND
    sprite = Sprite.ITEM_HEALING_WAND
    image_file_path = "resources/graphics/item_healing_wand.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(item_type, ItemEffect(item_type))
    name = "Healing wand"
    description = ["When you damage an enemy, gain +" + str(HEALTH_REGEN_BONUS) + " health regen for " +
                   "{:.0f}".format(BUFF_DURATION / 1000) + "s"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(item_type, item_data)
    register_buff_effect(BUFF_TYPE, BuffedByHealingWand)
    register_buff_text(BUFF_TYPE, "Healing wand")
