from typing import Dict, Union

from pythongame.core.common import *
from pythongame.core.game_state import GameState, Event
from pythongame.core.item_inventory import ItemEquipmentCategory, ItemWasActivated


class AbstractItemEffect:

    def __init__(self, item_id: ItemId):
        self.item_id = item_id
        self.item_type = ItemType[self.item_id.split(":")[0]]

    def apply_start_effect(self, game_state: GameState):
        pass

    def apply_middle_effect(self, game_state: GameState, time_passed: Millis):
        pass

    def apply_end_effect(self, game_state: GameState):
        pass

    def get_item_id(self):
        return self.item_id

    def item_handle_event(self, event: Event, game_state: GameState):
        pass

    def get_description(self) -> List[str]:
        raise Exception("No description defined for item " + str(self.get_item_id()))


def _get_description_of_stat_modifier(hero_stat: HeroStat, delta: Union[int, float]) -> str:
    if hero_stat == HeroStat.MAX_HEALTH:
        return "+" + str(delta) + " max health"
    elif hero_stat == HeroStat.HEALTH_REGEN:
        return "+" + str(delta) + " health regen"
    elif hero_stat == HeroStat.MAX_MANA:
        return "+" + str(delta) + " max mana"
    elif hero_stat == HeroStat.MANA_REGEN:
        return "+" + str(delta) + " mana regen"
    elif hero_stat == HeroStat.ARMOR:
        return str(delta) + " armor"
    elif hero_stat == HeroStat.MOVEMENT_SPEED:
        if delta >= 0:
            return "Increases movement speed by " + str(int(delta * 100)) + "%"
        else:
            return "Reduces movement speed by " + str(int(delta * 100)) + "%"
    elif hero_stat == HeroStat.DAMAGE:
        return "+" + str(int(round(delta * 100))) + "% damage"
    elif hero_stat == HeroStat.PHYSICAL_DAMAGE:
        return "+" + str(int(round(delta * 100))) + "% physical damage"
    elif hero_stat == HeroStat.MAGIC_DAMAGE:
        return "+" + str(int(round(delta * 100))) + "% magic damage"
    elif hero_stat == HeroStat.LIFE_STEAL:
        return "+" + str(int(delta * 100)) + "% life steal"
    elif hero_stat == HeroStat.BLOCK_AMOUNT:
        return str(delta) + " block"
    elif hero_stat == HeroStat.DODGE_CHANCE:
        return "+" + str(int(delta * 100)) + "% dodge"
    elif hero_stat == HeroStat.MAGIC_RESIST_CHANCE:
        return "+" + str(int(delta * 100)) + "% magic resist"
    else:
        raise Exception("Unhandled stat: " + str(hero_stat))


class StatModifyingItemEffect(AbstractItemEffect):
    def __init__(self, item_id: ItemId, stat_modifiers: Dict[HeroStat, Union[int, float]]):
        super().__init__(item_id)
        self.stat_modifiers = stat_modifiers

    def apply_start_effect(self, game_state: GameState):
        for stat, delta in self.stat_modifiers.items():
            game_state.modify_hero_stat(stat, delta)

    def apply_end_effect(self, game_state: GameState):
        for stat, delta in self.stat_modifiers.items():
            game_state.modify_hero_stat(stat, -delta)

    def get_description(self) -> List[str]:
        return [_get_description_of_stat_modifier(stat, delta) for (stat, delta) in self.stat_modifiers.items()]


class EmptyItemEffect(AbstractItemEffect):
    def __init__(self, item_id: ItemId):
        super().__init__(item_id)


_item_effects: Dict[ItemId, AbstractItemEffect] = {}


def register_item_effect(item_id: ItemId, effect: AbstractItemEffect):
    _item_effects[item_id] = effect


# Note this is handled differently compared to buffs
# There is only one effect instance per item type - having duplicate items with active effects may not be well supported
def get_item_effect(item_id: ItemId) -> AbstractItemEffect:
    return _item_effects[item_id]


def try_add_item_to_inventory(game_state: GameState, item_effect: AbstractItemEffect,
                              item_equipment_category: ItemEquipmentCategory) -> bool:
    result = game_state.player_state.item_inventory.try_add_item(item_effect, item_equipment_category)
    if result:
        if isinstance(result, ItemWasActivated):
            item_effect.apply_start_effect(game_state)
    return result is not None
