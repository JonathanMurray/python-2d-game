import random

from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_TYPE = ItemType.BLOOD_AMULET
HEALTH_ON_KILL_AMOUNT = 5
PROC_CHANCE = 0.3


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            if random.random() < PROC_CHANCE:
                player_receive_healing(HEALTH_ON_KILL_AMOUNT, game_state)


def register_blood_amulet():
    item_type = ItemType.BLOOD_AMULET
    register_custom_effect_item(
        item_type=item_type,
        item_level=4,
        ui_icon_sprite=UiIconSprite.ITEM_BLOOD_AMULET,
        sprite=Sprite.ITEM_BLOOD_AMULET,
        image_file_path="resources/graphics/item_blood_amulet.png",
        item_equipment_category=ItemEquipmentCategory.NECK,
        name="Blood Amulet",
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[],
        custom_description=[str(int(PROC_CHANCE * 100)) + "% on kill: gain " + str(HEALTH_ON_KILL_AMOUNT) + " health"]
    )
