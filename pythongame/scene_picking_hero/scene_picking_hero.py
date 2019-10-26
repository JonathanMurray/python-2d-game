import sys
from typing import Optional

import pygame

from pythongame.core.common import HeroId, SoundId
from pythongame.core.sound_player import play_sound
from pythongame.core.user_input import ActionExitGame
from pythongame.scene_picking_hero.user_input_picking_hero import get_picking_hero_user_input, ActionPickHeroChange, \
    ActionPickHeroAccept
from pythongame.scene_picking_hero.view_picking_hero import PickingHeroView

HEROES = [HeroId.MAGE, HeroId.WARRIOR, HeroId.ROGUE]


class PickingHeroScene:
    def __init__(self, view: PickingHeroView):
        self.view = view
        self.selected_hero_index = 0

    def run_one_frame(self) -> Optional[HeroId]:
        action = get_picking_hero_user_input()
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        elif isinstance(action, ActionPickHeroChange):
            self.selected_hero_index = (self.selected_hero_index + action.delta) % 3
            play_sound(SoundId.DIALOG)
        elif isinstance(action, ActionPickHeroAccept):
            return HEROES[self.selected_hero_index]

        self.view.render(HEROES, self.selected_hero_index)
        self.view.update_display()

        return None
