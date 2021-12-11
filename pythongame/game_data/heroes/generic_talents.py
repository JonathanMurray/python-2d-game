from typing import Union

from pythongame.core.common import HeroUpgradeId, UiIconSprite, HeroStat
from pythongame.core.game_data import register_ui_icon_sprite_path
from pythongame.core.game_state import GameState
from pythongame.core.hero_upgrades import register_hero_upgrade_effect, AbstractHeroUpgradeEffect
from pythongame.core.talents import TalentTierConfig, TalentTierOptionConfig


def register_generic_talents():
    register_hero_upgrade_effect(HeroUpgradeId.DAMAGE, ModifyHeroStat(HeroStat.DAMAGE, 0.1))
    register_hero_upgrade_effect(HeroUpgradeId.ARMOR, ModifyHeroStat(HeroStat.ARMOR, 1))
    register_hero_upgrade_effect(HeroUpgradeId.MAX_HEALTH, ModifyHeroStat(HeroStat.MAX_HEALTH, 10))
    register_hero_upgrade_effect(HeroUpgradeId.MAX_MANA, ModifyHeroStat(HeroStat.MAX_MANA, 10))
    register_hero_upgrade_effect(HeroUpgradeId.HEALTH_REGEN, ModifyHeroStat(HeroStat.HEALTH_REGEN, 0.5))
    register_hero_upgrade_effect(HeroUpgradeId.MANA_REGEN, ModifyHeroStat(HeroStat.MANA_REGEN, 0.5))
    register_ui_icon_sprite_path(UiIconSprite.TALENT_MOVE_SPEED, "resources/graphics/boots_of_haste.png")
    register_hero_upgrade_effect(HeroUpgradeId.MOVE_SPEED, ModifyHeroStat(HeroStat.MOVEMENT_SPEED, 0.1))
    register_hero_upgrade_effect(HeroUpgradeId.MAGIC_RESIST, ModifyHeroStat(HeroStat.MAGIC_RESIST_CHANCE, 0.05))


class ModifyHeroStat(AbstractHeroUpgradeEffect):

    def __init__(self, hero_stat: HeroStat, amount: Union[int, float]):
        self.hero_stat = hero_stat
        self.amount = amount

    def apply(self, game_state: GameState):
        game_state.modify_hero_stat(self.hero_stat, self.amount)

    def revert(self, game_state: GameState):
        game_state.modify_hero_stat(self.hero_stat, -self.amount)


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

TALENT_CHOICE_MOVE_SPEED_MAGIC_RESIST = TalentTierConfig(
    TalentTierOptionConfig("+ Movement speed", "Increases movement speed by 10%", HeroUpgradeId.MOVE_SPEED,
                           UiIconSprite.TALENT_MOVE_SPEED),
    TalentTierOptionConfig("+ Magic resist", "Increases your magic resist chance by 5%", HeroUpgradeId.MAGIC_RESIST,
                           UiIconSprite.ELIXIR_MAGIC_RESIST))
