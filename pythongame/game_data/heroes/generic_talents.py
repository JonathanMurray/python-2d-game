from pythongame.core.common import HeroUpgrade, UiIconSprite, HeroStat
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import register_hero_upgrade_effect
from pythongame.core.talents import TalentChoice, TalentChoiceOption


def register_generic_talents():
    register_hero_upgrade_effect(HeroUpgrade.DAMAGE, _upgrade_damage)
    register_hero_upgrade_effect(HeroUpgrade.ARMOR, _upgrade_armor)


def _upgrade_damage(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.DAMAGE, 0.1)


def _upgrade_armor(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.ARMOR, 1)


GENERIC_TALENT_CHOICE = TalentChoice(
    TalentChoiceOption("Armor", "Increases your armor by 1", HeroUpgrade.ARMOR, UiIconSprite.ITEM_ZULS_AEGIS),
    TalentChoiceOption("Damage", "Increases your damage bonus by 10%", HeroUpgrade.DAMAGE,
                       UiIconSprite.ITEM_ROYAL_SWORD))
