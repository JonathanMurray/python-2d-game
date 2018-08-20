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

def render_box(screen, box, camera_pos):
	pygame.draw.rect(screen, box.color, (box.x - camera_pos[0], box.y - camera_pos[1], box.w, box.h))

def ranges_overlap(a_min, a_max, b_min, b_max):
    return (a_min <= b_max) and (b_min <= a_max)

def rects_intersect(r1, r2):
    return ranges_overlap(r1.x, r1.x + r1.w, r2.x, r2.x + r2.w) \
    	and ranges_overlap(r1.y, r1.y + r1.h, r2.y, r2.y + r2.h)

BG_COLOR = (200,200,200)
SCREEN_SIZE = (500,500)
CAMERA_SIZE = (500, 470)
GAME_WORLD_SIZE = (600,600)

pygame.init()
pygame.font.init()
font = pygame.font.SysFont('Arial', 30)
screen = pygame.display.set_mode(SCREEN_SIZE)

camera_pos = (0, 0)
player = PlayerBox(Box((100, 100), (50, 50), (250,250,250)), Direction.RIGHT, 0, 9)
food_boxes = [Box((150, 350), (30, 30), (50, 200, 50)), Box((450, 300), (30, 30), (50, 200, 50))]
enemy_boxes = [Box((320, 220), (50, 50), (250, 0, 0))]
health = 3

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
		player.box.x = min(player.box.x + player.speed, GAME_WORLD_SIZE[0] - player.box.w)
	elif player.direction == Direction.UP:
		player.box.y = max(player.box.y - player.speed, 0)
	elif player.direction == Direction.DOWN:
		player.box.y = min(player.box.y + player.speed, GAME_WORLD_SIZE[1] - player.box.h)

	camera_pos = (min(max(player.box.x - CAMERA_SIZE[0] / 2, 0), GAME_WORLD_SIZE[0] - CAMERA_SIZE[0]), \
		min(max(player.box.y - CAMERA_SIZE[1] / 2, 0), GAME_WORLD_SIZE[1] - CAMERA_SIZE[1]))


	food_boxes_to_delete = []
	for box in food_boxes:
		if rects_intersect(player.box, box):
			food_boxes_to_delete.append(box)
			health += 1
	food_boxes = [b for b in food_boxes if b not in food_boxes_to_delete]

	enemy_boxes_to_delete = []
	for box in enemy_boxes:
		if rects_intersect(player.box, box):
			enemy_boxes_to_delete.append(box)
			health -= 1
	enemy_boxes = [b for b in enemy_boxes if b not in enemy_boxes_to_delete]

	screen.fill(BG_COLOR)
	render_box(screen, player.box, camera_pos)
	for box in food_boxes + enemy_boxes:
		render_box(screen, box, camera_pos)
	ui_text = "[" + str(health) + " HP]    [position (" + str(player.box.x) + ", " + str(player.box.y) + ")]"
	text_surface = font.render(ui_text, False, (0, 0, 0))
	screen.blit(text_surface, (100, 475))
	pygame.draw.rect(screen, (0, 0, 100), (0, 0, CAMERA_SIZE[0], CAMERA_SIZE[1]), 3)
	pygame.display.update()

