from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState

_upgrade_effects: Dict[HeroUpgrade, Callable[[GameState], Any]] = {}


def register_hero_upgrade_effect(hero_upgrade: HeroUpgrade, effect: Callable[[GameState], Any]):
    _upgrade_effects[hero_upgrade] = effect


def _apply_hero_upgrade(hero_upgrade: HeroUpgrade, game_state: GameState):
    if hero_upgrade in _upgrade_effects:
        effect = _upgrade_effects[hero_upgrade]
        effect(game_state)


def pick_talent(game_state: GameState, tier_index: int, option_index: int):
    name_of_picked, upgrade_picked = game_state.player_state.choose_talent(tier_index, option_index)
    _apply_hero_upgrade(upgrade_picked, game_state)
    return name_of_picked
