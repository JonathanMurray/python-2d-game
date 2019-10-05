import sys
from typing import Optional

import pygame

from pythongame.core.common import HeroId
from pythongame.core.user_input import ActionExitGame, get_picking_hero_user_input, ActionPickHero
from pythongame.core.view import View


class PickingHeroScene:
    def __init__(self, view: View):
        self.view = view

    def run_one_frame(self) -> Optional[HeroId]:
        action = get_picking_hero_user_input()
        if isinstance(action, ActionExitGame):
            pygame.quit()
            sys.exit()
        if isinstance(action, ActionPickHero):
            if action.number == 1:
                return HeroId.MAGE
            elif action.number == 2:
                return HeroId.WARRIOR
            elif action.number == 3:
                return HeroId.ROGUE
            else:
                raise Exception("Unhandled hero number: " + str(action.number))

        self.view.render_picking_hero_ui()
        self.view.update_display()

        return None
