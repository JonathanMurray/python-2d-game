#!/usr/bin/env python3


import pygame
import time
import sys
from enum import Enum

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

def render_box(screen, box):
	pygame.draw.rect(screen, box.color, box.rect())

def ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)

def rects_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)

BG_COLOR = (200,200,200)
PLAYER_COLOR = (200,100,100)
SCREEN_SIZE = (500,500)
PLAYER_SPEED = 9
PLAYER_SIZE = (50, 50)
PLAYER_START_POS = (100, 100)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
player = PlayerBox(Box(PLAYER_START_POS, PLAYER_SIZE, PLAYER_COLOR), Direction.RIGHT, 0, PLAYER_SPEED)
food_boxes = [Box((150, 350), (30, 30), (50, 50, 100)), Box((250, 300), (30, 30), (50, 100, 50))]

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

	food_boxes_to_delete = []
	for box in food_boxes:
		if rects_intersect(player.box, box):
			food_boxes_to_delete.append(box)
			# TODO: Reward for eating food
	food_boxes = [b for b in food_boxes if b not in food_boxes_to_delete]

	screen.fill(BG_COLOR)
	render_box(screen, player.box)
	for box in food_boxes:
		render_box(screen, box)
	pygame.display.update()

