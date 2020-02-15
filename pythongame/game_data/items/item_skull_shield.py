from pythongame.core.common import ItemType, Sprite, HeroStat, StatModifierInterval
from pythongame.core.damage_interactions import deal_player_damage_to_enemy, DamageType
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerBlockedEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

DAMAGE_AMOUNT = 5


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerBlockedEvent):
            deal_player_damage_to_enemy(game_state, event.npc_attacker, DAMAGE_AMOUNT, DamageType.MAGIC)


def register_skull_shield_item():
    item_type = ItemType.SKULL_SHIELD
    register_custom_effect_item(
        item_type=item_type,
        item_level=5,
        ui_icon_sprite=UiIconSprite.ITEM_SKULL_SHIELD,
        sprite=Sprite.ITEM_SKULL_SHIELD,
        image_file_path="resources/graphics/item_skull_shield.png",
        item_equipment_category=ItemEquipmentCategory.OFF_HAND,
        name="Skull shield",
        custom_description=["On block: deal " + str(DAMAGE_AMOUNT) + " magic damage to attacker"],
        stat_modifier_intervals=[StatModifierInterval(HeroStat.ARMOR, [2]),
                                 StatModifierInterval(HeroStat.BLOCK_AMOUNT, [6, 7, 8])],
        custom_effect=(ItemEffect())
    )
