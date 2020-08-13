from pythongame.core.abilities import AbilityData, register_ability_data
from pythongame.core.ability_effects import register_ability_effect, AbilityResult, AbilityWasUsedSuccessfully
from pythongame.core.common import HeroStat, StatModifierInterval, AbilityType, Millis
from pythongame.core.common import ItemType, Sprite
from pythongame.core.damage_interactions import player_receive_healing
from pythongame.core.game_data import UiIconSprite
from pythongame.core.game_state import Event, GameState, PlayerLostHealthEvent
from pythongame.core.item_effects import AbstractItemEffect
from pythongame.core.item_inventory import ItemEquipmentCategory
from pythongame.game_data.items.register_items_util import register_custom_effect_item

ITEM_NAME = "Lich armor"
ABILITY_TYPE = AbilityType.ITEM_LICH_ARMOR
ABILITY_MANA_AMOUNT = 50
ABILITY_DESCRIPTION = f"Restore {ABILITY_MANA_AMOUNT} mana"


class ItemEffect(AbstractItemEffect):

    def item_handle_event(self, event: Event, game_state: GameState):
        if isinstance(event, PlayerLostHealthEvent):
            absorb_amount = event.amount * 0.25
            if absorb_amount <= game_state.player_state.mana_resource.value:
                game_state.player_state.mana_resource.lose(absorb_amount)
                player_receive_healing(absorb_amount, game_state)


def _apply_ability(game_state: GameState) -> AbilityResult:
    game_state.player_state.mana_resource.gain(ABILITY_MANA_AMOUNT)
    return AbilityWasUsedSuccessfully()


def _register_ability():
    register_ability_effect(ABILITY_TYPE, _apply_ability)
    # TODO: sound effect
    ability_data = AbilityData(ITEM_NAME, UiIconSprite.ITEM_LICH_ARMOR, 0, Millis(60_000), ABILITY_DESCRIPTION,
                               sound_id=None, is_item_ability=True)
    register_ability_data(ABILITY_TYPE, ability_data)


def register_lich_armor_item():
    _register_ability()
    register_custom_effect_item(
        item_type=ItemType.LICH_ARMOR,
        item_level=8,
        ui_icon_sprite=UiIconSprite.ITEM_LICH_ARMOR,
        sprite=Sprite.ITEM_LICH_ARMOR,
        image_file_path="resources/graphics/item_lich_armor.png",
        item_equipment_category=ItemEquipmentCategory.CHEST,
        name=ITEM_NAME,
        custom_description=["25% of damage taken is instead drained from your mana",
                            "Active: " + ABILITY_DESCRIPTION],
        custom_effect=ItemEffect(),
        stat_modifier_intervals=[StatModifierInterval(HeroStat.MAX_MANA, [30]),
                                 StatModifierInterval(HeroStat.MAGIC_RESIST_CHANCE, [0.05])],
        is_unique=True,
        active_ability_type=ABILITY_TYPE
    )
