from pythongame.core.common import HeroUpgradeId, UiIconSprite, HeroStat
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import register_hero_upgrade_effect
from pythongame.core.talents import TalentTierConfig, TalentTierOptionConfig


def register_generic_talents():
    register_hero_upgrade_effect(HeroUpgradeId.DAMAGE, _upgrade_damage)
    register_hero_upgrade_effect(HeroUpgradeId.ARMOR, _upgrade_armor)
    register_hero_upgrade_effect(HeroUpgradeId.MAX_HEALTH, _upgrade_max_health)
    register_hero_upgrade_effect(HeroUpgradeId.MAX_MANA, _upgrade_max_mana)
    register_hero_upgrade_effect(HeroUpgradeId.HEALTH_REGEN, _upgrade_health_regen)
    register_hero_upgrade_effect(HeroUpgradeId.MANA_REGEN, _upgrade_mana_regen)


def _upgrade_damage(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.DAMAGE, 0.1)


def _upgrade_armor(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.ARMOR, 1)


def _upgrade_max_health(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.MAX_HEALTH, 10)


def _upgrade_max_mana(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.MAX_MANA, 10)


def _upgrade_health_regen(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.HEALTH_REGEN, 0.5)


def _upgrade_mana_regen(game_state: GameState):
    game_state.modify_hero_stat(HeroStat.MANA_REGEN, 0.5)


TALENT_CHOICE_ARMOR_DAMAGE = TalentTierConfig(
    TalentTierOptionConfig("+ Armor", "Increases your armor by 1", HeroUpgradeId.ARMOR, UiIconSprite.ITEM_ZULS_AEGIS),
    TalentTierOptionConfig("+ Damage", "Increases your damage bonus by 10%", HeroUpgradeId.DAMAGE,
                           UiIconSprite.ITEM_ROYAL_SWORD))
TALENT_CHOICE_HEALTH_MANA = TalentTierConfig(
    TalentTierOptionConfig("+ Health", "Increases your max health by 10", HeroUpgradeId.MAX_HEALTH,
                           UiIconSprite.POTION_HEALTH_LESSER),
    TalentTierOptionConfig("+ Mana", "Increases your max mana by 10", HeroUpgradeId.MAX_MANA,
                           UiIconSprite.POTION_MANA_LESSER))

TALENT_CHOICE_HEALTH_MANA_REGEN = TalentTierConfig(
    TalentTierOptionConfig("+ Health regen", "Increases your health regen by 0.5/s", HeroUpgradeId.HEALTH_REGEN,
                           UiIconSprite.POTION_HEALTH),
    TalentTierOptionConfig("+ Mana regen", "Increases your mana regen by 0.5/s", HeroUpgradeId.MANA_REGEN,
                           UiIconSprite.POTION_MANA))
