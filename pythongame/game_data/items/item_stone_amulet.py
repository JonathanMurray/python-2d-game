import random

from pythongame.core.buff_effects import register_buff_effect, get_buff_effect, \
    StatModifyingBuffEffect
from pythongame.core.common import ItemType, Sprite, Millis, PeriodicTimer, BuffType, HeroStat
from pythongame.core.game_data import UiIconSprite, register_buff_text
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState, NonPlayerCharacter
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.core.visual_effects import VisualCircle
from pythongame.core.world_entity import WorldEntity
from pythongame.game_data.items.register_items_util import register_custom_effect_item

PROC_CHANCE = 0.2
ARMOR_BONUS = 10
BUFF_TYPE = BuffType.PROTECTED_BY_STONE_AMULET
BUFF_DURATION = Millis(3000)


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < PROC_CHANCE:
                game_state.player_state.gain_buff_effect(get_buff_effect(BUFF_TYPE), BUFF_DURATION)


class ProtectedByStoneAmulet(StatModifyingBuffEffect):

    def __init__(self):
        super().__init__(BUFF_TYPE, {HeroStat.ARMOR: ARMOR_BONUS})
        self.timer = PeriodicTimer(Millis(300))

    def apply_middle_effect(self, game_state: GameState, buffed_entity: WorldEntity, buffed_npc: NonPlayerCharacter,
                            time_passed: Millis):
        if self.timer.update_and_check_if_ready(time_passed):
            game_state.game_world.visual_effects.append(
                VisualCircle((130, 100, 60), buffed_entity.get_center_position(), 20, 40, Millis(100), 1,
                             buffed_entity))


def register_stone_amulet_item():
    register_buff_effect(BUFF_TYPE, ProtectedByStoneAmulet)
    register_buff_text(BUFF_TYPE, "Protected")

    item_type = ItemType.STONE_AMULET
    register_custom_effect_item(
        item_type=item_type,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_STONE_AMULET,
        sprite=Sprite.ITEM_STONE_AMULET,
        image_file_path="resources/graphics/item_stone_amulet.png",
        item_equipment_category=ItemEquipmentCategory.NECK,
        name="Stone amulet",
        custom_description=[str(int(PROC_CHANCE * 100)) + "% on kill: gain " + str(ARMOR_BONUS) + " armor for " +
                            "{:.0f}".format(BUFF_DURATION / 1000) + "s"],
        stat_modifier_intervals=[],
        custom_effect=ItemEffect()
    )
