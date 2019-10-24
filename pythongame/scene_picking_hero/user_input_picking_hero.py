import pygame

from pythongame.core.user_input import ActionExitGame


class ActionPickHeroChange:
    def __init__(self, delta: int):
        self.delta = delta


class ActionPickHeroAccept:
    pass


def get_picking_hero_user_input():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return ActionExitGame()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_UP:
                return ActionPickHeroChange(-1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_DOWN:
                return ActionPickHeroChange(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return ActionPickHeroAccept()
