from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, PeriodicTimer
from pythongame.core.game_data import UiIconSprite, register_ui_icon_sprite_path, register_item_data, ItemData, \
    register_entity_sprite_initializer, ITEM_ENTITY_SIZE
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState, WorldEntity, \
    NonPlayerCharacter
from pythongame.core.image_loading import SpriteInitializer
from pythongame.core.item_effects import register_item_effect, AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle

SLOW_DURATION = Millis(2000)
SLOW_AMOUNT = 0.6

ITEM_TYPE = ItemType.FREEZING_GAUNTLET
BUFF_TYPE = BuffType.DEBUFFED_BY_FREEZING_GAUNTLET


class ItemEffect(AbstractItemEffect):

    def __init__(self, item_type: ItemType):
        self.item_type = item_type

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            event.enemy_npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), SLOW_DURATION)

    def get_item_type(self):
        return self.item_type


class DebuffedByFreezingGauntlet(AbstractBuffEffect):

    def __init__(self):
        self.graphics_timer = PeriodicTimer(Millis(400))

    def apply_start_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(-SLOW_AMOUNT)

    def apply_end_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter):
        buffed_entity.add_to_speed_multiplier(SLOW_AMOUNT)

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.graphics_timer.update_and_check_if_ready(time_passed):
            position = buffed_entity.get_center_position()
            visual_effect1 = VisualCircle((0, 40, 100), position, 9, 16, Millis(400), 2, buffed_entity)
            visual_effect2 = VisualCircle((0, 90, 180), position, 9, 16, Millis(500), 2, buffed_entity)
            game_state.visual_effects.append(visual_effect1)
            game_state.visual_effects.append(visual_effect2)

    def get_buff_type(self):
        return BUFF_TYPE


def register_freezing_gauntlet_item():
    ui_icon_sprite = UiIconSprite.ITEM_FREEZING_GAUNTLET
    sprite = Sprite.ITEM_FREEZING_GAUNTLET
    image_file_path = "resources/graphics/item_freezing_gauntlet.png"
    register_ui_icon_sprite_path(ui_icon_sprite, image_file_path)
    register_entity_sprite_initializer(sprite, SpriteInitializer(image_file_path, ITEM_ENTITY_SIZE))
    register_item_effect(ITEM_TYPE, ItemEffect(ITEM_TYPE))
    name = "Freezing Gauntlet"
    description = ["Slows your targets by " + str(int(SLOW_AMOUNT * 100)) + "% for " \
                   + "{:.1f}".format(SLOW_DURATION / 1000) + "s"]
    item_data = ItemData(ui_icon_sprite, sprite, name, description, ItemEquipmentCategory.MAIN_HAND)
    register_item_data(ITEM_TYPE, item_data)
    register_buff_effect(BUFF_TYPE, DebuffedByFreezingGauntlet)
