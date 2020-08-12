from typing import Dict

from pythongame.core.common import *
from pythongame.core.game_state import GameState


class AbstractHeroUpgradeEffect:
    def apply(self, game_state: GameState):
        raise Exception("Must override this method")

    def revert(self, game_state: GameState):
        raise Exception("Must override this method")


_upgrade_effects: Dict[HeroUpgradeId, AbstractHeroUpgradeEffect] = {}


def register_hero_upgrade_effect(hero_upgrade: HeroUpgradeId, effect: AbstractHeroUpgradeEffect):
    _upgrade_effects[hero_upgrade] = effect


def _apply_hero_upgrade(hero_upgrade: HeroUpgradeId, game_state: GameState):
    if hero_upgrade in _upgrade_effects:
        effect = _upgrade_effects[hero_upgrade]
        effect.apply(game_state)


def _revert_hero_upgrade(hero_upgrade: HeroUpgradeId, game_state: GameState):
    if hero_upgrade in _upgrade_effects:
        effect = _upgrade_effects[hero_upgrade]
        effect.revert(game_state)


def pick_talent(game_state: GameState, tier_index: int, option_index: int) -> str:
    name_of_picked, upgrade_picked = game_state.player_state.choose_talent(tier_index, option_index)
    _apply_hero_upgrade(upgrade_picked, game_state)
    return name_of_picked


def reset_talents(game_state: GameState):
    unpicked_hero_upgrade_ids = game_state.player_state.reset_talents()
    for upgrade_id in unpicked_hero_upgrade_ids:
        _revert_hero_upgrade(upgrade_id, game_state)
