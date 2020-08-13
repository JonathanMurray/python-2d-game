from typing import Optional, Dict, List

import pygame

from pythongame.core.common import UiIconSprite, Millis, SoundId, AbilityType


class AbilityData:
    def __init__(self, name: str, icon_sprite: UiIconSprite, mana_cost: int, cooldown: Millis, description: str,
                 sound_id: Optional[SoundId], is_item_ability: bool = False):
        self.name = name
        self.icon_sprite = icon_sprite
        self.mana_cost = mana_cost
        self.cooldown = cooldown
        self.description = description
        self.sound_id = sound_id
        self.is_item_ability = is_item_ability


class UserAbilityKey:
    def __init__(self, key_string: str, pygame_key):
        self.key_string = key_string
        self.pygame_key = pygame_key

    def __repr__(self):
        return "(" + self.key_string + ", " + str(self.pygame_key) + ")"


_user_ability_keys = [UserAbilityKey("Q", pygame.K_q),
                      UserAbilityKey("W", pygame.K_w),
                      UserAbilityKey("E", pygame.K_e),
                      UserAbilityKey("R", pygame.K_r)]
_item_ability_key = UserAbilityKey("T", pygame.K_t)

ABILITIES: Dict[AbilityType, AbilityData] = {}
KEYS_BY_ABILITY_TYPE: Dict[AbilityType, UserAbilityKey] = {}


def register_ability_data(ability_type: AbilityType, ability_data: AbilityData):
    ABILITIES[ability_type] = ability_data


def allocate_input_keys_for_abilities(ability_types: List[AbilityType]):
    KEYS_BY_ABILITY_TYPE.clear()

    non_item_ability_types = [a for a in ability_types if not ABILITIES[a].is_item_ability]
    for i, ability_type in enumerate(non_item_ability_types):
        KEYS_BY_ABILITY_TYPE[ability_type] = _user_ability_keys[i]

    item_ability_types = [a for a in ability_types if ABILITIES[a].is_item_ability]
    if item_ability_types:
        KEYS_BY_ABILITY_TYPE[item_ability_types[0]] = _item_ability_key
        if len(item_ability_types) > 1:
            print("WARN: More than 1 item ability")
