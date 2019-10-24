from typing import Dict, Callable, Any

from pythongame.core.common import *
from pythongame.core.game_state import GameState

_upgrade_effects: Dict[HeroUpgrade, Callable[[GameState], Any]] = {}


def register_hero_upgrade_effect(hero_upgrade: HeroUpgrade, effect: Callable[[GameState], Any]):
    _upgrade_effects[hero_upgrade] = effect


def apply_hero_upgrade(hero_upgrade: HeroUpgrade, game_state: GameState):
    if hero_upgrade in _upgrade_effects:
        effect = _upgrade_effects[hero_upgrade]
        effect(game_state)
