import sys
from typing import Optional

import pygame

from pythongame.core.common import HeroId, SoundId
from pythongame.core.sound_player import play_sound
from pythongame.core.user_input import ActionExitGame, get_picking_hero_user_input, ActionPickHeroChange, \
    ActionPickHeroAccept
from pythongame.core.view import View

HEROES = [HeroId.MAGE, HeroId.WARRIOR, HeroId.ROGUE]


class PickingHeroScene:
    def __init__(self, view: View):
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

        self.view.render_picking_hero_ui(HEROES, self.selected_hero_index)
        self.view.update_display()

        return None
