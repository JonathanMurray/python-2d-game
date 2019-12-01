from enum import Enum
from typing import Dict, List, Optional

from pythongame.core.common import HeroUpgrade, UiIconSprite


# The "config" classes are immutable and are determined from the hero you're playing
# The hierarchy is: talents --> talent tiers --> options with a tier

class TalentTierOptionConfig:
    def __init__(self, name: str, description: str, upgrade: HeroUpgrade, ui_icon_sprite: UiIconSprite):
        self.name = name
        self.description = description
        self.upgrade = upgrade
        self.ui_icon_sprite = ui_icon_sprite


class TalentTierConfig:
    def __init__(self, first_option: TalentTierOptionConfig, second_option: TalentTierOptionConfig):
        # For now, all tiers are made up of two options, but this may change in the future
        self.options = [first_option, second_option]


class TalentsConfig:
    def __init__(self, tiers_by_level: Dict[int, TalentTierConfig]):
        self.tiers_by_level: Dict[int, TalentTierConfig] = tiers_by_level

    def get_option(self, tier_index: int, option_index: int) -> TalentTierOptionConfig:
        tiers: List[TalentTierConfig] = [choice for level, choice in sorted(self.tiers_by_level.items())]
        tier = tiers[tier_index]
        return tier.options[option_index]

    def get_tiers_ordered_by_level(self) -> List[TalentTierConfig]:
        return [tier for level, tier in sorted(self.tiers_by_level.items())]


class TalentTierStatus(Enum):
    LOCKED = 1
    PENDING = 2
    PICKED = 3


class TalentTierState:
    def __init__(self, options: [TalentTierOptionConfig], status: TalentTierStatus, chosen_index: Optional[int],
                 required_level: int):
        self.options = options
        self.status = status
        self.picked_index = chosen_index
        self.required_level = required_level


class TalentsState:
    def __init__(self, talents_config: TalentsConfig):
        self._config = talents_config
        self.tiers: List[TalentTierState] = []
        for (level, tier_config) in sorted(self._config.tiers_by_level.items()):
            self.tiers.append(
                TalentTierState(tier_config.options, TalentTierStatus.LOCKED, None, level))

    def pick(self, tier_index: int, option_index: int) -> TalentTierOptionConfig:
        option = self._config.get_option(tier_index, option_index)
        tier = self.tiers[tier_index]
        tier.status = TalentTierStatus.PICKED
        tier.picked_index = option_index
        return option

    def has_unpicked_talents(self):
        pending_tiers = [tier for tier in self.tiers if tier.status == TalentTierStatus.PENDING]
        return len(pending_tiers) > 0

    def has_tier_for_level(self, level: int):
        return level in self._config.tiers_by_level

    def unlock_tier(self, new_level: int):
        for tier in self.tiers:
            if tier.required_level == new_level:
                tier.status = TalentTierStatus.PENDING
