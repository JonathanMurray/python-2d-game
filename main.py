#!/usr/bin/env python3


import pygame
import time
import sys
from enum import Enum

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

class Direction(Enum):
	LEFT = 1
	RIGHT = 2
	UP = 3
	DOWN = 4

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
player = Box(PLAYER_START_POS, PLAYER_SIZE)
direction = Direction.RIGHT
speed = 0
while(True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				direction = Direction.LEFT
				speed = PLAYER_SPEED
			elif event.key == pygame.K_RIGHT:
				direction = Direction.RIGHT
				speed = PLAYER_SPEED
			elif event.key == pygame.K_UP:
				direction = Direction.UP
				speed = PLAYER_SPEED
			elif event.key == pygame.K_DOWN:
				direction = Direction.DOWN
				speed = PLAYER_SPEED
		if event.type == pygame.KEYUP:
			speed = 0

	if direction == Direction.LEFT:
		player.x -= speed
	elif direction == Direction.RIGHT:
		player.x += speed
	elif direction == Direction.UP:
		player.y -= speed
	elif direction == Direction.DOWN:
		player.y += speed

	if player.x < 0:
		player.x = 0
	elif player.x > SCREEN_SIZE[0] - player.w:
		player.x = SCREEN_SIZE[0] - player.w
	if player.y < 0:
		player.y = 0
	elif player.y > SCREEN_SIZE[1] - player.h:
		player.y = SCREEN_SIZE[1] - player.h

	screen.fill(BG_COLOR)
	pygame.draw.rect(screen, PLAYER_COLOR, player.rect())
	pygame.display.update()

