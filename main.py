#!/usr/bin/env python3


import pygame
import time
import sys
from enum import Enum

BG_COLOR = (200,200,200)
PLAYER_COLOR = (200,100,100)
SCREEN_SIZE = (200,200)
PLAYER_SPEED = 9
PLAYER_SIZE = (50, 25)
PLAYER_START_POS = (100, 100)

class Box:
	def __init__(self, pos, size, color):
		self.x = pos[0]
		self.y = pos[1]
		self.w = size[0]
		self.h = size[1]
		self.color = color

	def rect(self):
		return (self.x, self.y, self.w, self.h)

class PlayerBox:
	def __init__(self, box, direction, speed, max_speed):
		self.box = box
		self.direction = direction
		self.speed = speed
		self.max_speed = max_speed

	def set_moving_in_dir(self, direction):
		self.direction = direction
		self.speed = self.max_speed

	def set_not_moving(self):
		self.speed = 0

class Direction(Enum):
	LEFT = 1
	RIGHT = 2
	UP = 3
	DOWN = 4

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
player = PlayerBox(Box(PLAYER_START_POS, PLAYER_SIZE, PLAYER_COLOR), Direction.RIGHT, 0, PLAYER_SPEED)

while(True):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				player.set_moving_in_dir(Direction.LEFT)
			elif event.key == pygame.K_RIGHT:
				player.set_moving_in_dir(Direction.RIGHT)
			elif event.key == pygame.K_UP:
				player.set_moving_in_dir(Direction.UP)
			elif event.key == pygame.K_DOWN:
				player.set_moving_in_dir(Direction.DOWN)
		if event.type == pygame.KEYUP:
			player.set_not_moving()

	if player.direction == Direction.LEFT:
		player.box.x = max(player.box.x - player.speed, 0)
	elif player.direction == Direction.RIGHT:
		player.box.x = min(player.box.x + player.speed, SCREEN_SIZE[0] - player.box.w)
	elif player.direction == Direction.UP:
		player.box.y = max(player.box.y - player.speed, 0)
	elif player.direction == Direction.DOWN:
		player.box.y = min(player.box.y + player.speed, SCREEN_SIZE[1] - player.box.h)

	screen.fill(BG_COLOR)
	pygame.draw.rect(screen, player.box.color, player.box.rect())
	pygame.display.update()

