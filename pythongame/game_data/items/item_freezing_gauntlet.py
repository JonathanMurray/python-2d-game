from pythongame.core.buff_effects import get_buff_effect, register_buff_effect, AbstractBuffEffect
from pythongame.core.common import ItemType, Sprite, BuffType, Millis, PeriodicTimer
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, PlayerDamagedEnemy, GameState, NonPlayerCharacter
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.items.register_items_util import register_custom_effect_item

SLOW_DURATION = Millis(2000)
SLOW_AMOUNT = 0.4

ITEM_TYPE = ItemType.FREEZING_GAUNTLET
BUFF_TYPE = BuffType.DEBUFFED_BY_FREEZING_GAUNTLET


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerDamagedEnemy):
            event.enemy_npc.gain_buff_effect(get_buff_effect(BUFF_TYPE), SLOW_DURATION)


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
            game_state.game_world.visual_effects.append(visual_effect1)
            game_state.game_world.visual_effects.append(visual_effect2)

    def get_buff_type(self):
        return BUFF_TYPE


def register_freezing_gauntlet_item():
    register_custom_effect_item(
        item_type=ITEM_TYPE,
        item_level=6,
        ui_icon_sprite=UiIconSprite.ITEM_FREEZING_GAUNTLET,
        sprite=Sprite.ITEM_FREEZING_GAUNTLET,
        image_file_path="resources/graphics/item_freezing_gauntlet.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Frost gauntlet",
        custom_description=["Slows your targets by " + str(int(SLOW_AMOUNT * 100)) + "% for " \
                            + "{:.1f}".format(SLOW_DURATION / 1000) + "s"],
        stat_modifier_intervals=[],
        custom_effect=ItemEffect()
    )

    register_buff_effect(BUFF_TYPE, DebuffedByFreezingGauntlet)
