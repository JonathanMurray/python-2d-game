from pythongame.core.common import HeroStat, StatModifierInterval
from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, EnemyDiedEvent, GameState
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

HEALTH_ON_KILL_AMOUNT = 1


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, EnemyDiedEvent):
            player_receive_healing(HEALTH_ON_KILL_AMOUNT, game_state)


def register_staff_of_fire_item():
    register_custom_effect_item(
        item_type=ItemType.STAFF_OF_FIRE,
        ui_icon_sprite=UiIconSprite.ITEM_STAFF_OF_FIRE,
        sprite=Sprite.ITEM_STAFF_OF_FIRE,
        image_file_path="resources/graphics/item_staff_of_fire.png",
        item_equipment_category=ItemEquipmentCategory.MAIN_HAND,
        name="Staff of the Phoenix",
        custom_description=["On kill: gain " + str(HEALTH_ON_KILL_AMOUNT) + " health"],
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MAGIC_DAMAGE, [0.25]),
                                 StatModifierInterval(HeroStat.MAX_MANA, [10])],
        is_unique=True
    )
