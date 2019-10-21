from typing import Dict, List, Optional

from pythongame.core.common import HeroUpgrade


class TalentChoiceOption:
    def __init__(self, name: str, upgrade: HeroUpgrade):
        self.name = name
        self.upgrade = upgrade


class TalentChoice:
    def __init__(self, first: TalentChoiceOption, second: TalentChoiceOption):
        self.first = first
        self.second = second


class TalentsState:
    def __init__(self, choices_by_level: Dict[int, TalentChoice]):
        self.choices_by_level: Dict[int, TalentChoice] = choices_by_level


class TalentChoiceGraphics:
    def __init__(self, choice: TalentChoice, chosen_index: Optional[int]):
        self.choice: TalentChoice = choice
        self.chosen_index: Optional[int] = chosen_index


class TalentsGraphics:
    def __init__(self, choices: List[TalentChoiceGraphics]):
        self.choice_graphics_items: List[TalentChoiceGraphics] = choices


def talents_graphics_from_state(talents: TalentsState, player_level: int,
                                chosen_talent_option_indices: List[int]) -> TalentsGraphics:
    shown_choices = []
    choices = [choice for level, choice in sorted(talents.choices_by_level.items())
               if player_level >= level]

    for i, choice in enumerate(choices):
        if i >= len(chosen_talent_option_indices):
            # player hasn't chosen a talent on this level yet
            shown_choices.append(TalentChoiceGraphics(choice, None))
            break
        shown_choices.append(TalentChoiceGraphics(choice, chosen_talent_option_indices[i]))

    return TalentsGraphics(shown_choices)
