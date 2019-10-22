from pythongame.core.common import HeroUpgrade
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import register_hero_upgrade_effect


def register_generic_talents():
    register_hero_upgrade_effect(HeroUpgrade.DAMAGE, _upgrade_damage)
    register_hero_upgrade_effect(HeroUpgrade.ARMOR, _upgrade_armor)


def _upgrade_damage(game_state: GameState):
    game_state.player_state.damage_modifier_bonus += 0.1


def _upgrade_armor(game_state: GameState):
    game_state.player_state.armor_bonus += 1
