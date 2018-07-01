#!/usr/bin/env python3


import pygame
import time

BG_COLOR = (200,200,200)
PLAYER_COLOR = (200,100,100)
SCREEN_SIZE = (500,500)
PLAYER_SPEED = 9
PLAYER_SIZE = (50, 50)
PLAYER_START_POS = (100, 400)

class Box:
	def __init__(self, start_pos, size):
		self.x = start_pos[0]
		self.y = start_pos[1]
		self.w = size[0]
		self.h = size[1]

	def rect(self):
		return (self.x, self.y, self.w, self.h)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
player = Box(PLAYER_START_POS, PLAYER_SIZE)
dx = 0
while(True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				dx = -PLAYER_SPEED
			elif event.key == pygame.K_RIGHT:
				dx = PLAYER_SPEED
		if event.type == pygame.KEYUP:
			dx = 0

	player.x += dx
	if player.x < 0:
		player.x = 0
	if player.x > SCREEN_SIZE[0] - player.w:
		player.x = SCREEN_SIZE[0] - player.w

	screen.fill(BG_COLOR)
	pygame.draw.rect(screen, PLAYER_COLOR, player.rect())
	pygame.display.update()

